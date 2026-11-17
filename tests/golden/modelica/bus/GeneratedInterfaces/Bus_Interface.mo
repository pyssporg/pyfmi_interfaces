within GeneratedInterfaces;

partial model Bus_Interface
  GeneratedInterfaces.Actuation actuation;
  GeneratedInterfaces.Orientation orientation_in;
  GeneratedInterfaces.Position position_in;
  GeneratedInterfaces.Orientation shared;
  GeneratedInterfaces.Orientation orientation_out;
  GeneratedInterfaces.Position position_out;
  GeneratedInterfaces.StatusPacket status;
end Bus_Interface;
