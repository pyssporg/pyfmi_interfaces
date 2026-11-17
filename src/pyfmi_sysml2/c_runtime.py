"""C++17 FMI 2.0 CoSimulation runtime for the generated C interfaces.

The runtime implements the FMI plumbing once per component from the same
variable map the C headers expose. Model behaviour is not generated: three
hooks in ``<stem>_model.cpp`` are created once and never rewritten, so an
interface change is absorbed by regenerating the plumbing while the
implementation stays untouched.

This module only writes source. It never compiles a translation unit and never
writes a build script; the build belongs to the consumer.
"""

from __future__ import annotations

from collections.abc import Sequence
from os import PathLike
from pathlib import Path

from pyfmi_sysml2.c_interface import (
    _architecture,
    component_header_name,
    generate_c_headers,
    header_stem,
)
from pyfmi_sysml2.headers import fmi2_headers
from pyfmi_sysml2.interface import (
    Component,
    components,
    export_identity,
    resolve_system,
    sanitize_identifier,
)

#: Every FMI 2.0 CoSimulation function the runtime emits. ``--omit`` is
#: validated against this set; a Model Exchange function is not part of it.
RUNTIME_FUNCTIONS = (
    "fmi2GetTypesPlatform",
    "fmi2GetVersion",
    "fmi2SetDebugLogging",
    "fmi2Instantiate",
    "fmi2FreeInstance",
    "fmi2SetupExperiment",
    "fmi2EnterInitializationMode",
    "fmi2ExitInitializationMode",
    "fmi2Terminate",
    "fmi2Reset",
    "fmi2GetReal",
    "fmi2GetInteger",
    "fmi2GetBoolean",
    "fmi2GetString",
    "fmi2SetReal",
    "fmi2SetInteger",
    "fmi2SetBoolean",
    "fmi2SetString",
    "fmi2GetFMUstate",
    "fmi2SetFMUstate",
    "fmi2FreeFMUstate",
    "fmi2SerializedFMUstateSize",
    "fmi2SerializeFMUstate",
    "fmi2DeSerializeFMUstate",
    "fmi2GetDirectionalDerivative",
    "fmi2EnterEventMode",
    "fmi2NewDiscreteStates",
    "fmi2EnterContinuousTimeMode",
    "fmi2CompletedIntegratorStep",
    "fmi2SetRealInputDerivatives",
    "fmi2GetRealOutputDerivatives",
    "fmi2DoStep",
    "fmi2CancelStep",
    "fmi2GetStatus",
    "fmi2GetRealStatus",
    "fmi2GetIntegerStatus",
    "fmi2GetBooleanStatus",
    "fmi2GetStringStatus",
)

#: The bundled FMI headers are copied below this directory in the output.
FMI2_DIRECTORY = "fmi2"


def runtime_source_name(stem: str) -> str:
    """File name of the generated FMI runtime translation unit."""
    return f"{stem}_fmi.cpp"


def hooks_header_name(stem: str) -> str:
    """File name of the generated model-hook declarations."""
    return f"{stem}_hooks.h"


def model_source_name(stem: str) -> str:
    """File name of the user-owned model implementation."""
    return f"{stem}_model.cpp"


def _label(package: str, component: Component, *, direct: bool) -> str:
    """The human label the C header uses for the same component."""
    if direct and package == component.name:
        return package
    return f"{package}.{component.name}"


def _omit_names(omit: Sequence[str] | str) -> tuple[str, ...]:
    """Flatten, validate, and canonicalise ``--omit`` names.

    A name may be passed on its own or in a comma-separated value; both forms
    are accepted and may be mixed. Unknown names are refused with the complete
    set of names the generator emits.
    """
    if isinstance(omit, str):
        omit = (omit,)
    requested: list[str] = []
    for item in omit:
        for part in item.split(","):
            name = part.strip()
            if not name:
                raise ValueError(
                    "empty name in --omit; pass fmi2Foo or fmi2Foo,fmi2Bar"
                )
            requested.append(name)

    valid = set(RUNTIME_FUNCTIONS)
    unknown = sorted(set(requested) - valid)
    if unknown:
        raise ValueError(
            "unknown --omit name(s): "
            + ", ".join(unknown)
            + "; valid names: "
            + ", ".join(RUNTIME_FUNCTIONS)
        )
    return tuple(sorted(set(requested)))


def _hooks_header(package: str, component: Component, stem: str, *, direct: bool) -> str:
    """Text of ``<stem>_hooks.h``, the model side of the runtime contract."""
    guard = f"{sanitize_identifier(stem)}_HOOKS_H"
    label = _label(package, component, direct=direct)
    return "\n".join(
        [
            f"#ifndef {guard}",
            f"#define {guard}",
            "",
            f'#include "{component_header_name(package, component.name, direct=direct)}"',
            '#include "fmi2/fmi2Functions.h"',
            "",
            f"/* Model hooks for {label}. Implemented in {model_source_name(stem)}. */",
            "",
            "#ifdef __cplusplus",
            'extern "C" {',
            "#endif",
            "",
            f"fmi2Status {stem}_model_initialize({stem}_Instance* instance);",
            "",
            f"fmi2Status {stem}_model_do_step(",
            f"    {stem}_Instance* instance, fmi2Real current_communication_point,",
            "    fmi2Real communication_step_size);",
            "",
            f"fmi2Status {stem}_model_terminate({stem}_Instance* instance);",
            "",
            "#ifdef __cplusplus",
            "}",
            "#endif",
            "",
            f"#endif  /* {guard} */",
            "",
        ]
    )


def _model_source(package: str, component: Component, stem: str, *, direct: bool) -> str:
    """Initial text of ``<stem>_model.cpp``, written only when absent."""
    label = _label(package, component, direct=direct)
    return "\n".join(
        [
            f"/* Model behaviour for {label}.",
            "   The generator creates this file once and never rewrites it. */",
            f'#include "{hooks_header_name(stem)}"',
            "",
            f"fmi2Status {stem}_model_initialize({stem}_Instance* instance) {{",
            "  (void)instance;",
            "  /* TODO: initialise derived model state from its parameters and inputs.",
            "     Parameters already hold their start values; a no-op is valid. */",
            "  return fmi2OK;",
            "}",
            "",
            f"fmi2Status {stem}_model_do_step(",
            f"    {stem}_Instance* instance, fmi2Real current_communication_point,",
            "    fmi2Real communication_step_size) {",
            "  (void)instance;",
            "  (void)current_communication_point;",
            "  (void)communication_step_size;",
            "  /* TODO: advance the model by communication_step_size. */",
            "  return fmi2Error;",
            "}",
            "",
            f"fmi2Status {stem}_model_terminate({stem}_Instance* instance) {{",
            "  (void)instance;",
            "  return fmi2OK;",
            "}",
            "",
        ]
    )


def _is_parameter_source(component: Component, stem: str) -> str:
    """A switch over the VR enum naming the parameter value references."""
    upper_stem = sanitize_identifier(stem)
    lines = [
        f"static bool {stem}_is_parameter_vr(fmi2ValueReference vr) {{",
        "  switch (vr) {",
    ]
    for variable in component.variables:
        if variable.causality != "parameter":
            continue
        label = f"{upper_stem}_VR_{sanitize_identifier(variable.name)}"
        lines.extend([f"    case {label}:", "      return true;"])
    lines.extend(["    default:", "      return false;", "  }", "}"])
    return "\n".join(lines)


def _helpers(package: str, component: Component, stem: str) -> str:
    """Private handle, logging, and batch-validation helpers of one runtime."""
    return "\n".join(
        [
            f"struct {stem}_Handle {{",
            f"  {stem}_Instance* model;",
            "  const fmi2CallbackFunctions* callbacks;",
            "  fmi2Boolean logging_on;",
            "  bool initialized;",
            "  bool terminated;",
            "  fmi2Real start_time;",
            "  fmi2Real last_successful_time;",
            "  fmi2Status last_do_step_status;",
            "};",
            "",
            f"static {stem}_Handle* {stem}_handle(fmi2Component c) {{",
            f"  return static_cast<{stem}_Handle*>(c);",
            "}",
            "",
            f"static void {stem}_log(fmi2Component c, fmi2Status status,",
            "                       const char* message) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr || !h->logging_on) {",
            "    return;",
            "  }",
            "  if (h->callbacks == nullptr || h->callbacks->logger == nullptr) {",
            "    return;",
            "  }",
            f'  h->callbacks->logger(h->callbacks->componentEnvironment, "{component.name}",',
            '                       status, "", message);',
            "}",
            "",
            f"static void {stem}_instantiate_log(",
            "    const fmi2CallbackFunctions* functions, fmi2Boolean logging_on,",
            "    const char* message) {",
            "  if (!logging_on || functions == nullptr ||",
            "      functions->logger == nullptr) {",
            "    return;",
            "  }",
            f'  functions->logger(functions->componentEnvironment, "{component.name}",',
            '                    fmi2Error, "", message);',
            "}",
            "",
            _is_parameter_source(component, stem),
            "",
            f"static fmi2Status {stem}_check_batch(",
            "    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,",
            f"    {package}_DataType expected, bool writing) {{",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  if (nvr > 0 && vr == nullptr) {",
            f'    {stem}_log(c, fmi2Error, "value reference array is null");',
            "    return fmi2Error;",
            "  }",
            "  for (size_t i = 0; i < nvr; ++i) {",
            f"    if (vr[i] >= {stem}_VrCount) {{",
            f'      {stem}_log(c, fmi2Error, "value reference is out of range");',
            "      return fmi2Error;",
            "    }",
            f"    const {package}_VrMapping& entry = h->model->vr_map[vr[i]];",
            "    if (entry.data == nullptr) {",
            f'      {stem}_log(c, fmi2Error, "value reference has no storage");',
            "      return fmi2Error;",
            "    }",
            "    if (entry.type != expected) {",
            f'      {stem}_log(c, fmi2Error, "value reference has a different type");',
            "      return fmi2Error;",
            "    }",
            "    if (writing && !entry.writable) {",
            f'      {stem}_log(c, fmi2Error, "value reference is not writable");',
            "      return fmi2Error;",
            "    }",
            f"    if (writing && {stem}_is_parameter_vr(vr[i]) && h->initialized) {{",
            f'      {stem}_log(c, fmi2Error,',
            '                  "parameter cannot be set after initialization");',
            "      return fmi2Error;",
            "    }",
            "  }",
            "  return fmi2OK;",
            "}",
            "",
        ]
    )


_CPP_TYPES = {
    "REAL": "fmi2Real",
    "INTEGER": "fmi2Integer",
    "BOOLEAN": "fmi2Boolean",
    "STRING": "fmi2String",
}


def _get_definition(
    stem: str,
    function: str,
    tag: str,
    type_tag: str,
    body: Sequence[str],
) -> str:
    """A ``fmi2Get*`` definition with the shared validation prelude."""
    lines = [
        f"FMI2_Export fmi2Status {function}(",
        "    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,",
        f"    {_CPP_TYPES[tag]} value[]) {{",
        "  if (nvr > 0 && value == nullptr) {",
        f'    {stem}_log(c, fmi2Error, "{function}: value array is null");',
        "    return fmi2Error;",
        "  }",
        f"  fmi2Status status = {stem}_check_batch(c, vr, nvr, {type_tag}, false);",
        "  if (status != fmi2OK) {",
        "    return status;",
        "  }",
        f"  {stem}_Handle* h = {stem}_handle(c);",
        "  for (size_t i = 0; i < nvr; ++i) {",
    ]
    lines.extend(f"    {line}" for line in body)
    lines.extend(["  }", "  return fmi2OK;", "}"])
    return "\n".join(lines)


def _set_definition(
    stem: str,
    function: str,
    tag: str,
    type_tag: str,
    body: Sequence[str],
    *,
    prelude: Sequence[str] = (),
) -> str:
    """A ``fmi2Set*`` definition with the shared validation prelude."""
    lines = [
        f"FMI2_Export fmi2Status {function}(",
        "    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,",
        f"    const {_CPP_TYPES[tag]} value[]) {{",
        "  if (nvr > 0 && value == nullptr) {",
        f'    {stem}_log(c, fmi2Error, "{function}: value array is null");',
        "    return fmi2Error;",
        "  }",
        f"  fmi2Status status = {stem}_check_batch(c, vr, nvr, {type_tag}, true);",
        "  if (status != fmi2OK) {",
        "    return status;",
        "  }",
    ]
    lines.extend(prelude)
    lines.extend(
        [
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  for (size_t i = 0; i < nvr; ++i) {",
        ]
    )
    lines.extend(f"    {line}" for line in body)
    lines.extend(["  }", "  return fmi2OK;", "}"])
    return "\n".join(lines)


def _get_set_definitions(package: str, stem: str) -> dict[str, str]:
    """The eight typed getter and setter definitions."""
    upper = sanitize_identifier(package)
    definitions: dict[str, str] = {}

    definitions["fmi2GetReal"] = _get_definition(
        stem,
        "fmi2GetReal",
        "REAL",
        f"{upper}_DATA_REAL",
        ["value[i] = *static_cast<fmi2Real*>(h->model->vr_map[vr[i]].data);"],
    )
    definitions["fmi2GetInteger"] = _get_definition(
        stem,
        "fmi2GetInteger",
        "INTEGER",
        f"{upper}_DATA_INTEGER",
        ["value[i] = *static_cast<fmi2Integer*>(", "    h->model->vr_map[vr[i]].data);"],
    )
    definitions["fmi2GetBoolean"] = _get_definition(
        stem,
        "fmi2GetBoolean",
        "BOOLEAN",
        f"{upper}_DATA_BOOLEAN",
        [
            "value[i] = *static_cast<bool*>(h->model->vr_map[vr[i]].data)",
            "              ? fmi2True : fmi2False;",
        ],
    )
    definitions["fmi2GetString"] = _get_definition(
        stem,
        "fmi2GetString",
        "STRING",
        f"{upper}_DATA_STRING",
        [
            "value[i] = static_cast<std::string*>(",
            "    h->model->vr_map[vr[i]].data)->c_str();",
        ],
    )

    definitions["fmi2SetReal"] = _set_definition(
        stem,
        "fmi2SetReal",
        "REAL",
        f"{upper}_DATA_REAL",
        ["*static_cast<fmi2Real*>(h->model->vr_map[vr[i]].data) = value[i];"],
    )
    definitions["fmi2SetInteger"] = _set_definition(
        stem,
        "fmi2SetInteger",
        "INTEGER",
        f"{upper}_DATA_INTEGER",
        ["*static_cast<fmi2Integer*>(h->model->vr_map[vr[i]].data) = value[i];"],
    )
    definitions["fmi2SetBoolean"] = _set_definition(
        stem,
        "fmi2SetBoolean",
        "BOOLEAN",
        f"{upper}_DATA_BOOLEAN",
        [
            "*static_cast<bool*>(h->model->vr_map[vr[i]].data) =",
            "    (value[i] != fmi2False);",
        ],
    )
    definitions["fmi2SetString"] = _set_definition(
        stem,
        "fmi2SetString",
        "STRING",
        f"{upper}_DATA_STRING",
        ["*static_cast<std::string*>(h->model->vr_map[vr[i]].data) = value[i];"],
        prelude=[
            "  for (size_t i = 0; i < nvr; ++i) {",
            "    if (value[i] == nullptr) {",
            f'      {stem}_log(c, fmi2Error, "fmi2SetString: value is null");',
            "      return fmi2Error;",
            "    }",
            "  }",
        ],
    )

    return definitions


def _definitions(package: str, component: Component, stem: str) -> dict[str, str]:
    """Every generated function definition, keyed by its FMI name."""
    upper_stem = sanitize_identifier(stem)
    guid = f"{upper_stem}_GUID"
    definitions: dict[str, str] = {}

    definitions["fmi2GetTypesPlatform"] = "\n".join(
        [
            "FMI2_Export const char* fmi2GetTypesPlatform(void) {",
            '  return "default";',
            "}",
        ]
    )
    definitions["fmi2GetVersion"] = "\n".join(
        [
            "FMI2_Export const char* fmi2GetVersion(void) {",
            '  return "2.0";',
            "}",
        ]
    )
    definitions["fmi2SetDebugLogging"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2SetDebugLogging(",
            "    fmi2Component c, fmi2Boolean loggingOn, size_t nCategories,",
            "    const fmi2String categories[]) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  (void)nCategories;",
            "  (void)categories;",
            "  h->logging_on = loggingOn;",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2Instantiate"] = "\n".join(
        [
            "FMI2_Export fmi2Component fmi2Instantiate(",
            "    fmi2String instanceName, fmi2Type fmuType, fmi2String fmuGUID,",
            "    fmi2String fmuResourceLocation,",
            "    const fmi2CallbackFunctions* functions, fmi2Boolean visible,",
            "    fmi2Boolean loggingOn) {",
            "  (void)instanceName;",
            "  (void)fmuResourceLocation;",
            "  (void)visible;",
            "  if (fmuType != fmi2CoSimulation) {",
            f"    {stem}_instantiate_log(functions, loggingOn,",
            '        "fmi2Instantiate: only fmi2CoSimulation is supported");',
            "    return nullptr;",
            "  }",
            f"  if (fmuGUID == nullptr || std::strcmp(fmuGUID, {guid}) != 0) {{",
            f"    {stem}_instantiate_log(functions, loggingOn,",
            '        "fmi2Instantiate: GUID does not match");',
            "    return nullptr;",
            "  }",
            f"  {stem}_Instance* model = new (std::nothrow) {stem}_Instance{{}};",
            "  if (model == nullptr) {",
            f"    {stem}_instantiate_log(functions, loggingOn,",
            '        "fmi2Instantiate: cannot allocate the model");',
            "    return nullptr;",
            "  }",
            f"  {stem}_initialize_vr_map(model);",
            f"  {stem}_Handle* handle = new (std::nothrow) {stem}_Handle{{}};",
            "  if (handle == nullptr) {",
            "    delete model;",
            f"    {stem}_instantiate_log(functions, loggingOn,",
            '        "fmi2Instantiate: cannot allocate the instance");',
            "    return nullptr;",
            "  }",
            "  handle->model = model;",
            "  handle->callbacks = functions;",
            "  handle->logging_on = loggingOn;",
            "  handle->last_do_step_status = fmi2OK;",
            "  return static_cast<fmi2Component>(handle);",
            "}",
        ]
    )
    definitions["fmi2FreeInstance"] = "\n".join(
        [
            "FMI2_Export void fmi2FreeInstance(fmi2Component c) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return;",
            "  }",
            "  delete h->model;",
            "  delete h;",
            "}",
        ]
    )
    definitions["fmi2SetupExperiment"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2SetupExperiment(",
            "    fmi2Component c, fmi2Boolean toleranceDefined, fmi2Real tolerance,",
            "    fmi2Real startTime, fmi2Boolean stopTimeDefined, fmi2Real stopTime) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  (void)toleranceDefined;",
            "  (void)tolerance;",
            "  (void)stopTimeDefined;",
            "  (void)stopTime;",
            "  h->start_time = startTime;",
            "  h->last_successful_time = startTime;",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2EnterInitializationMode"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2EnterInitializationMode(fmi2Component c) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2ExitInitializationMode"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2ExitInitializationMode(fmi2Component c) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  h->initialized = false;",
            f"  fmi2Status status = {stem}_model_initialize(h->model);",
            "  if (status == fmi2OK) {",
            "    h->initialized = true;",
            "  } else {",
            f"    {stem}_log(c, status,",
            '                  "fmi2ExitInitializationMode: initialization failed");',
            "  }",
            "  return status;",
            "}",
        ]
    )
    definitions["fmi2Terminate"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2Terminate(fmi2Component c) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  if (h->terminated) {",
            "    return fmi2OK;",
            "  }",
            "  h->terminated = true;",
            f"  fmi2Status status = {stem}_model_terminate(h->model);",
            "  if (status != fmi2OK) {",
            f'    {stem}_log(c, status, "fmi2Terminate: model termination failed");',
            "  }",
            "  return status;",
            "}",
        ]
    )
    definitions["fmi2Reset"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2Reset(fmi2Component c) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            f"  *h->model = {stem}_Instance{{}};",
            f"  {stem}_initialize_vr_map(h->model);",
            "  h->initialized = false;",
            "  h->terminated = false;",
            "  h->start_time = 0.0;",
            "  h->last_successful_time = 0.0;",
            "  h->last_do_step_status = fmi2OK;",
            "  return fmi2OK;",
            "}",
        ]
    )

    definitions.update(_get_set_definitions(package, stem))

    unsupported = (
        (
            "fmi2GetFMUstate",
            ["    fmi2Component c, fmi2FMUstate* FMUstate) {"],
            ["  (void)FMUstate;"],
        ),
        (
            "fmi2SetFMUstate",
            ["    fmi2Component c, fmi2FMUstate FMUstate) {"],
            ["  (void)FMUstate;"],
        ),
        (
            "fmi2FreeFMUstate",
            ["    fmi2Component c, fmi2FMUstate* FMUstate) {"],
            ["  (void)FMUstate;"],
        ),
        (
            "fmi2SerializedFMUstateSize",
            [
                "    fmi2Component c, fmi2FMUstate FMUstate, size_t* size) {"
            ],
            ["  (void)FMUstate;", "  (void)size;"],
        ),
        (
            "fmi2SerializeFMUstate",
            [
                "    fmi2Component c, fmi2FMUstate FMUstate,",
                "    fmi2Byte serializedState[], size_t size) {",
            ],
            [
                "  (void)FMUstate;",
                "  (void)serializedState;",
                "  (void)size;",
            ],
        ),
        (
            "fmi2DeSerializeFMUstate",
            [
                "    fmi2Component c, const fmi2Byte serializedState[],",
                "    size_t size, fmi2FMUstate* FMUstate) {",
            ],
            [
                "  (void)serializedState;",
                "  (void)size;",
                "  (void)FMUstate;",
            ],
        ),
        (
            "fmi2GetDirectionalDerivative",
            [
                "    fmi2Component c, const fmi2ValueReference vUnknown_ref[],",
                "    size_t nUnknown, const fmi2ValueReference vKnown_ref[],",
                "    size_t nKnown, const fmi2Real dvKnown[],",
                "    fmi2Real dvUnknown[]) {",
            ],
            [
                "  (void)vUnknown_ref;",
                "  (void)nUnknown;",
                "  (void)vKnown_ref;",
                "  (void)nKnown;",
                "  (void)dvKnown;",
                "  (void)dvUnknown;",
            ],
        ),
        (
            "fmi2SetRealInputDerivatives",
            [
                "    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,",
                "    const fmi2Integer order[], const fmi2Real value[]) {",
            ],
            [
                "  (void)vr;",
                "  (void)nvr;",
                "  (void)order;",
                "  (void)value;",
            ],
        ),
        (
            "fmi2GetRealOutputDerivatives",
            [
                "    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,",
                "    const fmi2Integer order[], fmi2Real value[]) {",
            ],
            [
                "  (void)vr;",
                "  (void)nvr;",
                "  (void)order;",
                "  (void)value;",
            ],
        ),
    )
    for name, signature, body in unsupported:
        lines = [f"FMI2_Export fmi2Status {name}(", *signature]
        lines.extend(
            [
                f"  {stem}_Handle* h = {stem}_handle(c);",
                "  if (h == nullptr) {",
                "    return fmi2Error;",
                "  }",
            ]
        )
        lines.extend(body)
        lines.extend(
            [
                f'  {stem}_log(c, fmi2Error, "{name}: not supported");',
                "  return fmi2Error;",
                "}",
            ]
        )
        definitions[name] = "\n".join(lines)

    definitions["fmi2EnterEventMode"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2EnterEventMode(fmi2Component c) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2NewDiscreteStates"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2NewDiscreteStates(",
            "    fmi2Component c, fmi2EventInfo* fmi2eventInfo) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr || fmi2eventInfo == nullptr) {",
            f'    {stem}_log(c, fmi2Error, "fmi2NewDiscreteStates: null argument");',
            "    return fmi2Error;",
            "  }",
            "  *fmi2eventInfo = fmi2EventInfo{};",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2EnterContinuousTimeMode"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2EnterContinuousTimeMode(",
            "    fmi2Component c) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2CompletedIntegratorStep"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2CompletedIntegratorStep(",
            "    fmi2Component c, fmi2Boolean noSetFMUStatePriorToCurrentPoint,",
            "    fmi2Boolean* enterEventMode, fmi2Boolean* terminateSimulation) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr || enterEventMode == nullptr ||",
            "      terminateSimulation == nullptr) {",
            f'    {stem}_log(c, fmi2Error,',
            '                  "fmi2CompletedIntegratorStep: null argument");',
            "    return fmi2Error;",
            "  }",
            "  (void)noSetFMUStatePriorToCurrentPoint;",
            "  *enterEventMode = fmi2False;",
            "  *terminateSimulation = fmi2False;",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2DoStep"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2DoStep(",
            "    fmi2Component c, fmi2Real currentCommunicationPoint,",
            "    fmi2Real communicationStepSize,",
            "    fmi2Boolean noSetFMUStatePriorToCurrentPoint) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  (void)noSetFMUStatePriorToCurrentPoint;",
            "  if (communicationStepSize <= 0.0) {",
            f'    {stem}_log(c, fmi2Error, "fmi2DoStep: step size is not positive");',
            "    return fmi2Error;",
            "  }",
            f"  fmi2Status status = {stem}_model_do_step(",
            "      h->model, currentCommunicationPoint, communicationStepSize);",
            "  h->last_do_step_status = status;",
            "  if (status == fmi2OK) {",
            "    h->last_successful_time =",
            "        currentCommunicationPoint + communicationStepSize;",
            "  } else {",
            f'    {stem}_log(c, status, "fmi2DoStep: model step failed");',
            "  }",
            "  return status;",
            "}",
        ]
    )
    definitions["fmi2CancelStep"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2CancelStep(fmi2Component c) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr) {",
            "    return fmi2Error;",
            "  }",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2GetStatus"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2GetStatus(",
            "    fmi2Component c, const fmi2StatusKind s, fmi2Status* value) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr || value == nullptr) {",
            f'    {stem}_log(c, fmi2Error, "fmi2GetStatus: null argument");',
            "    return fmi2Error;",
            "  }",
            "  if (s == fmi2DoStepStatus) {",
            "    *value = h->last_do_step_status;",
            "  } else if (s == fmi2PendingStatus) {",
            "    *value = fmi2OK;  /* no asynchronous step is pending */",
            "  } else {",
            f'    {stem}_log(c, fmi2Error, "fmi2GetStatus: unsupported status kind");',
            "    return fmi2Error;",
            "  }",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2GetRealStatus"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2GetRealStatus(",
            "    fmi2Component c, const fmi2StatusKind s, fmi2Real* value) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr || value == nullptr) {",
            f'    {stem}_log(c, fmi2Error, "fmi2GetRealStatus: null argument");',
            "    return fmi2Error;",
            "  }",
            "  if (s != fmi2LastSuccessfulTime) {",
            f'    {stem}_log(c, fmi2Error,',
            '                  "fmi2GetRealStatus: unsupported status kind");',
            "    return fmi2Error;",
            "  }",
            "  *value = h->last_successful_time;",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2GetIntegerStatus"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2GetIntegerStatus(",
            "    fmi2Component c, const fmi2StatusKind s, fmi2Integer* value) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr || value == nullptr) {",
            f'    {stem}_log(c, fmi2Error, "fmi2GetIntegerStatus: null argument");',
            "    return fmi2Error;",
            "  }",
            "  (void)s;",
            f'  {stem}_log(c, fmi2Error, "fmi2GetIntegerStatus: unsupported");',
            "  return fmi2Error;",
            "}",
        ]
    )
    definitions["fmi2GetBooleanStatus"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2GetBooleanStatus(",
            "    fmi2Component c, const fmi2StatusKind s, fmi2Boolean* value) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr || value == nullptr) {",
            f'    {stem}_log(c, fmi2Error, "fmi2GetBooleanStatus: null argument");',
            "    return fmi2Error;",
            "  }",
            "  if (s != fmi2Terminated) {",
            f'    {stem}_log(c, fmi2Error,',
            '                  "fmi2GetBooleanStatus: unsupported status kind");',
            "    return fmi2Error;",
            "  }",
            "  *value = h->terminated ? fmi2True : fmi2False;",
            "  return fmi2OK;",
            "}",
        ]
    )
    definitions["fmi2GetStringStatus"] = "\n".join(
        [
            "FMI2_Export fmi2Status fmi2GetStringStatus(",
            "    fmi2Component c, const fmi2StatusKind s, fmi2String* value) {",
            f"  {stem}_Handle* h = {stem}_handle(c);",
            "  if (h == nullptr || value == nullptr) {",
            f'    {stem}_log(c, fmi2Error, "fmi2GetStringStatus: null argument");',
            "    return fmi2Error;",
            "  }",
            "  (void)s;",
            f'  {stem}_log(c, fmi2Error, "fmi2GetStringStatus: unsupported");',
            "  return fmi2Error;",
            "}",
        ]
    )

    return definitions


def _fmi_source(
    package: str,
    component: Component,
    stem: str,
    *,
    direct: bool,
    omitted: tuple[str, ...],
) -> str:
    """Text of the generated ``<stem>_fmi.cpp``."""
    label = _label(package, component, direct=direct)
    definitions = _definitions(package, component, stem)

    banner = [
        "/*",
        f" * Generated FMI 2.0 CoSimulation runtime for {label}.",
        " * Do not edit manually; regenerate with `pyfmi c-runtime`.",
        f" * Model behaviour lives in {model_source_name(stem)}.",
        " */",
    ]
    banner.extend(f"/* omitted via --omit: {name} */" for name in omitted)

    parts = [
        "\n".join(banner),
        "",
        "#include <cstring>",
        "#include <new>",
        "#include <string>",
        "",
        '#include "fmi2/fmi2Functions.h"',
        f'#include "{component_header_name(package, component.name, direct=direct)}"',
        f'#include "{hooks_header_name(stem)}"',
        "",
        _helpers(package, component, stem).rstrip(),
        "",
        'extern "C" {',
        "",
    ]
    for name in RUNTIME_FUNCTIONS:
        if name in omitted:
            continue
        parts.extend([definitions[name], ""])
    parts.extend(["}", ""])
    return "\n".join(parts)


def generate_c_runtime(
    source,
    output_dir: str | PathLike[str],
    *,
    composition: str | None = None,
    prefix: str | None = None,
    base_index: int = 0,
    omit: Sequence[str] | str = (),
) -> list[Path]:
    """Write the C interface headers and the C++17 FMI runtime into ``output_dir``.

    Each exported component gets ``<stem>_fmi.cpp`` (regenerated),
    ``<stem>_hooks.h`` (regenerated), and ``<stem>_model.cpp`` (created only
    when absent). The headers the runtime includes are regenerated through
    :func:`generate_c_headers`, and the bundled FMI 2.0 headers are copied to
    ``fmi2/`` on every run.

    ``omit`` skips the definition of the named FMI functions and records each
    omission in the generated banner; names may be repeated or comma-separated.
    An unknown name raises ``ValueError`` naming the complete emitted set.

    The returned paths are in a stable order: the common header, the component
    headers sorted by file name, then for each component (sorted by name) the
    runtime source, the hooks header, and the model source when it was created;
    the three ``fmi2/`` copies come last, sorted by file name.
    """
    architecture = _architecture(source)
    package = prefix or architecture.package_name
    system = resolve_system(architecture, composition)
    exported = components(
        architecture, composition=composition, base_index=base_index
    )
    direct = export_identity(architecture, system).direct
    omitted = _omit_names(omit)

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    written = generate_c_headers(
        architecture,
        directory,
        composition=composition,
        prefix=prefix,
        base_index=base_index,
    )

    for item in exported:
        stem = header_stem(package, item.name, direct=direct)

        runtime = directory / runtime_source_name(stem)
        runtime.write_text(
            _fmi_source(
                package, item, stem, direct=direct, omitted=omitted
            ),
            encoding="utf-8",
        )
        written.append(runtime)

        hooks = directory / hooks_header_name(stem)
        hooks.write_text(
            _hooks_header(package, item, stem, direct=direct),
            encoding="utf-8",
        )
        written.append(hooks)

        model = directory / model_source_name(stem)
        if not model.exists():
            model.write_text(
                _model_source(package, item, stem, direct=direct),
                encoding="utf-8",
            )
            written.append(model)

    target = directory / FMI2_DIRECTORY
    target.mkdir(parents=True, exist_ok=True)
    for header in fmi2_headers():
        copy = target / header.name
        copy.write_bytes(header.read_bytes())
        written.append(copy)

    return written
