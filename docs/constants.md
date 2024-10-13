## Constants

The following constants are available as float point numbers, identical to the values in CGS unit as listed in the 'Value' column:

```
========== ============== ================ =========================
   Name        Value            Unit       Description
========== ============== ================ =========================
    G       6.674300e-08    cm3 / (g s2)   Gravitational constant
   N_A      6.022141e+23      1 / mol      Avogadro's number
    R       8.314463e+07   erg / (K mol)   Gas constant
   Ryd      1.097373e+05       1 / cm      Rydberg constant
    a0      5.291772e-09         cm        Bohr radius
  alpha     7.297353e-03                   Fine-structure constant
   atm      1.013250e+06       P / s       Standard atmosphere
  b_wien    2.897772e-01        cm K       Wien wavelength displacement law constant
    c       2.997925e+10       cm / s      Speed of light in vacuum
    g0      9.806650e+02      cm / s2      Standard acceleration of gravity
    h       6.626070e-27       erg s       Planck constant
   hbar     1.054572e-27       erg s       Reduced Planck constant
   k_B      1.380649e-16      erg / K      Boltzmann constant
   m_e      9.109384e-28         g         Electron mass
   m_n      1.674927e-24         g         Neutron mass
   m_p      1.672622e-24         g         Proton mass
 sigma_T    6.652459e-25        cm2        Thomson scattering cross-section
 sigma_sb   5.670374e-05    g / (K4 s3)    Stefan-Boltzmann constant
    u       1.660539e-24         g         Atomic mass
 GM_earth   3.986004e+20      cm3 / s2     Nominal Earth mass parameter
  GM_jup    1.266865e+23      cm3 / s2     Nominal Jupiter mass parameter
  GM_sun    1.327124e+26      cm3 / s2     Nominal solar mass parameter
  L_bol0    3.012800e+35      erg / s      Luminosity for absolute bolometric magnitude 0
  L_sun     3.828000e+33      erg / s      Nominal solar luminosity
 M_earth    5.972168e+27         g         Earth mass
  M_jup     1.898125e+30         g         Jupiter mass
  M_sun     1.988410e+33         g         Solar mass
 R_earth    6.378100e+08         cm        Nominal Earth equatorial radius
  R_jup     7.149200e+09         cm        Nominal Jupiter equatorial radius
  R_sun     6.957000e+10         cm        Nominal solar radius
    au      1.495979e+13         cm        Astronomical Unit
   kpc      3.085678e+21         cm        Kiloparsec
    pc      3.085678e+18         cm        Parsec
========== ============== ================ =========================
```

The following units are available:

```python
{
  'Length': ['m', 'cm', 'mm', 'um', 'nm', 'Angstrom', 'km', 'au', 'AU', 'pc', 'kpc', 'Mpc', 'lyr',],
  'Mass': ['kg', 'g', 'M_sun', 'Msun'],
  'Density': ['mpcc'],
  'Time': ['s', 'yr', 'Myr', 'Gyr',],
  'Energy': ['J', 'erg', 'eV', 'keV', 'MeV', 'GeV'],
  'Power': ['W'],
  'Pressure': ['Pa', 'bar', 'mbar'],
  'Frequency': ['Hz', 'kHz', 'MHz', 'GHz',],
  'EM': ['esu', 'Gauss'],
  'Temperature': ['K',],
  'Angular size': ['deg', 'radian', 'arcmin', 'arcsec', 'arcsec2', 'sr'],
  'Astronomy': ['Lsun', 'Jy', 'mJy', 'MJy', 'a_rad'],
  'Composite': ['m2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3']
}
```