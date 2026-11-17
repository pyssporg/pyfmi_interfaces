within GeneratedInterfaces;

partial model Controller_Interface
  parameter Real gains[2] = {1, 2.5};
  parameter String label = "nominal";
  GeneratedInterfaces.Command command;
  GeneratedInterfaces.Throttle throttle;
  GeneratedInterfaces.Status status;
end Controller_Interface;
