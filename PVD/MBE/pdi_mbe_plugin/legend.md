### Legend for file format in EPIC

* Both wOP and MV comes from the eurotherm PID controller
  * MV: measured value
    * wOP: working output power (%) 
* GC: growth chamber
* MF: mass flow control
* IG: ion gauge
* PG: pressure gauge
* LL: load lock
* MC: middle chamber (garage)
* PID: for temperature
* MIG: multi-ion gauge
* O: oxygen
* sub: substrate temperature
* BEP: beam equivalent pressure
* SP: set point
* Trol: trolley, moveable sample garage
* Pyro: substrate temperature measured by pyrometer instead plasma power.
    * Pyrometer shutter is operated manually
* messages: what is important is "Location Tab"
* Light: NOT USED ANYMORE, shows if the plasma is ignited or not.

EPIC (custom software that is used in MBE systems of PDI), programs recipes, during the recipe user can change how the growth is done, irrespective to the recipe so messages is not so important other than the Location tab, as it gives the substrate and holder information.

Second Revision
  * O.Forward.MV (W) - oxygen plasma gun RF power that supplied.
  * O.Reflect.MV (W) - oxygen plasma gun RF power that reflected.
    * the substraction of these two gives us the net power delivered to plasma.
  * O.MF.MV (sccm) - oxygen flow rate to oxygen cavity.
  * Upper 