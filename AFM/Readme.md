# Atomic force microscopy / scanning probe microscopy
[Atomic force microscopy](https://en.wikipedia.org/wiki/Atomic_force_microscopy) was developed in the 1980s. First published by [Binnig et al. in Physical Review Letters](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.56.930).
In the following decade a series of instruments had become available and employed in a wide field of experiments spanning from physics through materials science to cellular biphysics.

# Historical comments
The idea of measuring colloidal forces and topography are not completely new. However, the first device that had managed to reproducively measure colloidal forces on surfaces was reported in [1969 by Israelachvili, Tabor and Winterton](https://www.jstor.org/stable/2416454?origin=JSTOR-pdf#metadata_info_tab_contents), which lead to the development of the surface forces apparatus (SFA).

Another direction was characterizing surface topography on the microscopic scale, which was leading to [profilometers](https://en.wikipedia.org/wiki/Profilometer) based on a contact stylus or optical interference.

# Disambiguation
A key element of an AFM is the positioning system used to scan the surface and move the probe above the surface. This is in general is based on the [piezoelectric effect](https://en.wikipedia.org/wiki/Piezoelectricity) or more its inverse, where one applies a voltage on a piezoelectric crystal and that changes its length (deforms) as a consequence.

Now, the name implies that we are investigating forces acting on a probe at atomic scale. To detect forces, we usually convert the force to deformation using a sensor. The original paper described a microscopic leaf spring with a tip attached to its surface. The tip was interacing with the surface, causing a deflection of the microscopic spring, which deflection was detected using a capacitive sensor system.

## contact mode AFM
This method is what today is known as contact mode atomic force microscopy. Even in this simple case we have two modes of operation possible:
 - scan the head (or sample) in the XY plane and follow the deflection of the sensor;
 - decide on a certain deflection level (and thus force) and keep it constant, adjusting the distance of the probe from the surface accordingly, and record the changes in the Z direction.

The former easily results in breaking the probe, and the latter is the one what is today used in most instruments.

## friction force images
When the scan is performed with a fast axis in the direction perpendicular of the long axis of the cantilever, the interaction to the surface also causes a twist of the cantilever, which is detected (most commonly) as the left-right signal on the segmented photodetector. Comparing this signal between scanning a line forwards and backwards (trace and retrace), we get information characteristic to the interaction (friction).

## non-contact or intermittent-contact modes
To find a less invasive method to image soft surfaces, another way was developed. Leaf springs always have a resonance frequency if oscillated. Oscillating the probe near or at its reasonance, the amplitude and phase (between the driving oscilation and the actual motion of the cantilever) will be sensitive to the interaction to the surface.

Though non-contact mode is very sensitive and non-invasive, it turned out to be difficult to use, prone to drift and noise.

An alternative solution was to bring the oscillating probe to touch the surface, causing a decrease in the oscillation amplitude let us say at about 90% of the free oscillation. Then maintain this oscillation amplitude in the feedback loop and scan the topography of the surface.

## other ways of probing
The topography measured with a feedback system will always depend on the real topography of the surface (which is the hard wall limit of the material) and interaction between the probe and the material on / of the surface.

Thus, if we have a way of tuning this interaction using:
 - tips of specific chemistry (functionalized or fabricated of specific materials)
 - conductive or semiconductive tips and controlled potential / current
 - magnetic material based tips
 - etc.

## quantitative imaging
A little different method has become available with the development of computers and data processing in thepast few decades. This method measures the force - separation distance curves at every XY point on the surface and determines various mechanical parameters, such as elasticity (Young's modulus) or maximal force of adhesion. The QI mode produces large data sets and is claimed to be very quantitative.

# Force detection
In all cases the key sensor is a microscopic leaf-spring, a cantilever with submillimeter length and a few micrometers of thickness. Its deflection can be detected in various ways.

The original system used a cantilever coated with a metal film, and a capacitive sensor to see its vertical deflection.

Moderns devices mostly use a light pointer, the displacement of light reflected from the back side of the cantilever projected onto a segmented photodiode. Using such an optical detector allows for a very sensitive detection of changes in bending (tilt of the 'mirror').

# Calibration
Thus, detectors provide some kind of electic signal proportional to the force acting on the cantilever. Usually this signal has to be first converted to an actual deflection (using the sensor response) and then to force (using the spring constant).

## sensor response
The simplest way of detecting the sensor response is to push the probe to a hard surface when any motion of the back end of the cantilever directly relates to the sensor signal, and the slope of this straight curve indicates the sensor response.

Alternatively the oscillation amplitude of a free standing cantilever with known spring constant (usually derived from its geometry and material properties) can be employed.

## spring constant
There are a set of possibilities to estimate the spring constant of a cantilever:
 - estimate it based on the material properties and the geometry of the cantilever
 - thermal oscillation / oscillation resonance of the cantilever
 - apply a set of particles with known weight and measure deflection
 - bend the cantilever agains a known cantilever and follow the bending of both

From these, the first two are the most common ones nowadays, and both have their problems of accuracy.

### geometric correction
There is a deviation between the two methods of detecting deflection / spring constant, coming from the fact that the deformation shape is different between the two methods. This may result in a typical 20-30% deviation between the real value and the measured value both for the spring constant or the sensor response.

The correction also depends on the geometry of the cantilever, most commonly a rectangular beam or an A-shaped spring.

## calibration for friction
The two key parameters are similar, but different than above. Again we need a sensor response describing the relation between the detected signal and the twist angle, then this angle and the actual torque.


# Force measurements
While it is usually a different way of operating an AFM, generating force-distance curves, it is directly employed in quantitative imaging mode.

Force-distance curves are measured driving the vertical position of the probe either moving the sample or the probe. This direction is denoted usually as Z-axis.

There are two main modes used in this measurement:
 - driving the Z-positioner with a predefined speed and detect the force (and Z-position)
 - maintain a constant force by moving the Z-position, the so called force-clamp mode

In both modes the probe is pushed to the surface up to a predefined maximal force, and then the actual measurement begins.
Force-distance scans still report the X,Y piezo position of the head, thus it is possible to create maps of derived model parameters.

# Reporting scans
From the description above it is clear that not all experiments can be described using the same parameters. There is a major difference between contact and non-contact methods. All may require to have a proper sensor response and spring constant calibration, but the latter also require a free oscillation resonance measured. Other SPM methods will require further parameters, but these can be easily appended.

The instruments actually record numeric values from analog to digital (A/D) converters, which are first converted to voltage or current based on hardware parameters, then to physical units based on calibration of the components.

## piezo positions
Piezoelectric stacs show a non-linear characteristics in their voltage - position relation. Usually this is approximated as a second order polynomial, and is calibrated by the manufacturer using interferomentic position measurements.

Since these stacks age, thus their parameters change with time, every system provides means to tune these parameters based on scans of reference samples (provided by the manufacturer).
Another way of countering this problem is that many models developed after about 2000 includes capacitive sensor based position detection to measure the actual position of the various piezo actuators.
Capacitive sensors are less accurate than the interferometric method, but also robust and stable. (Less accurate meaning typically +/- 1-2 nm.)

Thus, the devices often record the piezo positions based on the voltage applied to the piezo stacks, and another set as 'measured' positions.

## file formats
Most systems report data in proprietary file formats. These may contain all necessary information about the scanner, calibration parameters, etc., but reading them can be complicated.

### Gwyddeon
The open source software [Gwyddion](https://github.com/christian-sahlmann/gwyddion) is capable of reading many of the available file formats, and provides an OSS output version for other users.
The original [website](https://gwyddion.net/) is down for a few months now, the active page is at [Sourceforge](https://sourceforge.net/p/gwyddion/blog/).

## Common reported parameters
### cantilevers / probes
 - probe name and supplier, e.g. PPP-NCLR tapping mode probe from Nanoandmore
 - probe geometry type: beam shape
 - probe material (nominal): Si
 - coating: Al backside film
 - nominal length: 225 micrometer
 - nominal resonance frequency: 190 kHz
 - nominal spring constant: 48 N/m
 - nominal tip radius: 7 nm

Not every imaging requires full calibration of the probes, but if that was performed, report:
 - sensore response
 - spring constant
 - what method was used to calibrate
 - calibration data
 - temperature

If the probe was modified or cleaned prior measurement that is an experiment to be
referenced here.

### scan parameters
 - set point
 - image size in micrometers
 - image size in pixels
 - scanning frequency (one full trace and retrace scan / second)
 - scanning speed (optional)
 - integral gain
 - proportional gain
 - differential gain (if available)
 - dynamic parameter adjustment used (e.g. scanAssyst)

### for non-contact modes
 - free oscillation frequency in kHz
 - set oscillation frequency in kHs
 - free oscillation amplitude
(We can assume that phase was set to zero at free oscillation close to the surface.)

### for QI mode or force modulation mode
 - force oscillation frequency
 - force oscillation amplitude
