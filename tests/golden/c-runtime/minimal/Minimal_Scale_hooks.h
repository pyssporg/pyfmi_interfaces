#ifndef MINIMAL_SCALE_HOOKS_H
#define MINIMAL_SCALE_HOOKS_H

#include "Minimal_Scale.h"
#include "fmi2/fmi2Functions.h"

/* Model hooks for Minimal.Scale. Implemented in Minimal_Scale_model.cpp. */

#ifdef __cplusplus
extern "C" {
#endif

fmi2Status Minimal_Scale_model_initialize(Minimal_Scale_Instance* instance);

fmi2Status Minimal_Scale_model_do_step(
    Minimal_Scale_Instance* instance, fmi2Real current_communication_point,
    fmi2Real communication_step_size);

fmi2Status Minimal_Scale_model_terminate(Minimal_Scale_Instance* instance);

#ifdef __cplusplus
}
#endif

#endif  /* MINIMAL_SCALE_HOOKS_H */
