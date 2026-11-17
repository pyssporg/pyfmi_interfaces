within GeneratedInterfaces;

partial model Tank_Interface
  parameter Real capacity = 3160;
  parameter Real reserve = 0.08;
  GeneratedInterfaces.Rate supply;
  GeneratedInterfaces.LevelState level;
end Tank_Interface;
