/* Model behaviour for Minimal.Scale.
   The generator creates this file once and never rewrites it. */
#include "Minimal_Scale_hooks.h"

fmi2Status Minimal_Scale_model_initialize(Minimal_Scale_Instance* instance) {
  (void)instance;
  /* TODO: initialise derived model state from its parameters and inputs.
     Parameters already hold their start values; a no-op is valid. */
  return fmi2OK;
}

fmi2Status Minimal_Scale_model_do_step(
    Minimal_Scale_Instance* instance, fmi2Real current_communication_point,
    fmi2Real communication_step_size) {
  (void)instance;
  (void)current_communication_point;
  (void)communication_step_size;
  /* TODO: advance the model by communication_step_size. */
  return fmi2Error;
}

fmi2Status Minimal_Scale_model_terminate(Minimal_Scale_Instance* instance) {
  (void)instance;
  return fmi2OK;
}
