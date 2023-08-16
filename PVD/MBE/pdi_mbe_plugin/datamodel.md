* **Substrate Holder** (*object*) - to be described, what shape, what different substrate is in what positions etc.
	* **Substrate Holder** Positioning Angle (Only GrowthRun) in reference to RHEED electron gun. Needs an eye reference on top of Substrate Holder.
		* **EPIC angle:** when substrate holder's reference mark is oriented towards the RHEED electron gun (ex: can be case in EPIC software, the angle is 43 but the angle between RHEED electron gun and subsrate holder's reference mark is 0.)
* **Substrate** (*object*)
		* **Position Information** relative Substrate Holder (Only GrowthRun)
			* Substrates positions in holder.
			* Substrate in-plane reference orientation # used for epitaxy, as basis for in-plane epitaxial relation to the Holder
		* **Compound**
			*  chemical formula: # e.g., Ga2O3 - the chemical formula
			- DOPANT: # can be multiple dopants
				- element: # chem. symbol, e.g. Fe
				- concentration: # cm^-3, e.g., 3e18
		* **Crystal** 
			*  **space group:** # or some other accepted descriptor of the xtal structure, use a reserved one for amorphous
			* **angles**: # alpha, beta, gamma
			* **lattice parameters:** # a, b, c
			- **surface orientation**: 
				- hkl: # e.g. (1 0 0)
				- offcut:
					- degrees: #, e.g. 2
					- towards:  e.g. (001)
		* **Geometry** (*macroshape*)
			* Type of Geometry
				* cylindrical
					* full-wafer
					* quarter-wafer
				* rectangular
					* parallelepiped
					* square
			* Thickness
			* in-plane dimensions
				* cyclindrical
					* diameter (mm, inch)
				* rectangular
					* length (mm)
					* width (mm)
					* angle (mm)
			* **in-plane reference orientation** # used for epitaxy, as basis for in-plane epitaxial relation to the Holder, in relation to planes 
				* **h,k,l**
				* **scratch direction (?)**
				* text description from user
* **Substrate Preparation**
	* **Dicing**
	* Etching
	* Annealing
	* Backside Coating
* Loadlock
	* pressure
	* baking temperature & duration
* Middle Chamber (Garage) (not needed rn)
	* Position (not needed)
		* Sample
* GrowthRun
	* Starts from LocationTab timestamp for parser.py
	* Substrate Oxygen Plasma Treatment
		* Plasma Source
			* Physical Position relative to surface normal
				* Euler Angle (specific to any source, plasma source, effusion source, evaporator etc.)
				* Distance
			* Mass Flow Device (O)
				* Gas
					* N
						* vendor name, batch number etc.
						* purity
					* O
						* vendor name, batch number etc.
						* purity
						* isotope num.
							* 18O2
							* 16O2 
					* Ar
						* vendor name, batch number etc.
						* purity
				* related log file: 
					* O.Forward.MV
					* O.Reflect.MV
					* O.MF.MV
			* Mass Flow Device (N)
				* Gas
					* N
						* vendor name, batch number etc.
						* purity
					* O
						* vendor name, batch number etc.
						* purity
						* isotope num.
							* 18O2
							* 16O2 
					* Ar
						* vendor name, batch number etc.
						* purity
				* related log file: 
					* N.Forward.MV
					* N.Reflect.MV
					* N.MF.MV
	* Substrate Temperature (stays same for the all growth process.)
			* related log files
				* Sub.PID.MV
					* thermocouple that place in between substrate heater and substrate itself.
				* Pyro.PID.MV
					* Substrate temperature measured by pyrometer, there is a manual shutter to expose pyrometer to growth chamber.
	* First Growth Step
		* Cell
			* Shutter (boolean)
				* related log file
					* **Shutters**
			* Crucible
				* Material
				* Vendor, batch number etc.
				* misc.
			* Source Material
				* monochemical
				* mixtures of chemicals
			* Source Vapor (Outgoing Material)
				* composition (ex: Ga) (it is reaction product of Source Material, change of phase, form of suboxide etc.)
				* flux at the substrate
					* specified in three different flavors:
						* m**-2 * sec**-1 
						* beam equivalent pressure (BEP) mbar/tor etc.
						* equivalent growth rate (angstrom per sec)
							* we need to specify the material that is grown (ex:Ga2O3)
							* rate
			* Cell Type
				* Single-Filament
					* Temperature
						* related log files:
							* xxx.PID.MV
							* xxx.PID.wOP (not sure if we need it)
				* Dual-Filament
					* Base Temperature
						* related log files:
							* xxx.PID.MV
							* xxx.PID.wOP (not sure if we need it)
					* Hotlip Temperature ( tip )
						* related log files:
							* xxxHL.PID.MV
							* xxxHL.PID.wOP  (not sure if we need it)
			* Physical Position relative to surface normal
				* Euler Angle (specific to any source, plasma source, effusion source, evaporator etc.)
				* Distance
		* Oxygen Plasma Source
				* Physical Position relative to surface normal
					* Euler Angle (specific to any source, plasma source, effusion source, evaporator etc.)
					* Distance
				* Mass Flow Device (O)
					* Gas
						* N
							* vendor name, batch number etc.
							* purity
						* O
							* vendor name, batch number etc.
							* purity
							* isotope num.
								* 18O2
								* 16O2 
						* Ar
							* vendor name, batch number etc.
							* purity
					* related log file: 
						* O.Forward.MV
						* O.Reflect.MV
						* O.MF.MV
				* Mass Flow Device (N)
					* Gas
						* N
							* vendor name, batch number etc.
							* purity
						* O
							* vendor name, batch number etc.
							* purity
							* isotope num.
								* 18O2
								* 16O2 
						* Ar
							* vendor name, batch number etc.
							* purity
					* related log file: 
						* N.Forward.MV
						* N.Reflect.MV
						* N.MF.MV
	* in-situ measurements:
		*  Chamber Ambient
			* vacuum gauges (ion-gauge)
			* mass spectrometers
		* laser reflectometry 
			* angle of laser in respect to substrate normal
			* laser
				* set wavelength 
				* polarization
			* photodiode
				* measured intensity
					* **related log files:**
						* 2306101435_m83732.dat (sec, intensity)
		* RHEED
			* electron gun
				* set electron energy
				* incidence angle
				* emission current
				* deflection parameters
					* lenses, deflector etc...
			* EPIC angle
			* acquisition parameters
			* RHEED data (from camera#1 directed to RHEED screen)
				* image (png, jpg etc.)
				* video
					* rotation speed
		* camera #2