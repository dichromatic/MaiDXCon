using MelonLoader;
using HarmonyLib;
using IO;
using System.IO.Ports;
using System.Reflection;

namespace MyMod
{
    [HarmonyPatch(typeof(NewTouchPanel), "Open")]
    public class SerialPatch : MelonMod
    {
        static bool Prefix(uint ____monitorIndex, string[] ___PortName, ref SerialPort ____serialPort, int ___BaudRate)
        {
            {
                try
                {
                    ____serialPort = new SerialPort(___PortName[____monitorIndex], ___BaudRate, Parity.None, 8, StopBits.One);
                    ____serialPort.ReadTimeout = 1;
                    ____serialPort.WriteTimeout = 1000;
                    ____serialPort.DtrEnable = true;
                    ____serialPort.Open();
                }
                catch
                {
                }
            }
            return false;
        }
        public override void OnInitializeMelon()
        {
            //FieldInfo serialPort = typeof(NewTouchPanel).GetField("_serialPort", BindingFlags.NonPublic | BindingFlags.Instance);
            //object[] dtrEnabled = serialPort.GetCustomAttributes(typeof(bool), false);
            LoggerInstance.Msg($"DTR Enabled");
        }
    }
}