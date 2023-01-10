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

