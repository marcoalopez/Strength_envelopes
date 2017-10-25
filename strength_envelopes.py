# ============================================================================ #
#                                                                              #
#    Strenght envelopes                                                        #
#    A Python script for plotting lithosphere and crust strength envelopes     #
#                                                                              #
#    Copyright (c) 2017-present   Marco A. Lopez-Sanchez                       #
#                                                                              #
#    This Source Code Form is subject to the terms of the Mozilla Public       #
#    License, v. 2.0. If a copy of the MPL was not distributed with this       #
#    file, You can obtain one at http://mozilla.org/MPL/2.0/.                  #
#                                                                              #
#    Covered Software is provided under this License on an “AS IS” BASIS,      #
#    WITHOUT WARRANTY OF ANY KIND, either expressed, implied, or statutory,    #
#    including, without limitation, warranties that the Covered Software is    #
#    FREE OF DEFECTS, merchantable, fit for a particular purpose or            #
#    non-infringing. The entire risk as to the quality and performance         #
#    of the Covered Software is with You. Should any Covered Software prove    #
#    defective in any respect, You (not any Contributor) assume the cost of    #
#    any necessary servicing, repair, or correction. This disclaimer of        #
#    warranty constitutes an essential part of this License. No use of any     #
#    Covered Software is authorized under this License except under this       #
#    disclaimer.                                                               #
#                                                                              #
#    Version alpha                                                             #
#    For details see: https://github.com/marcoalopez/Strength_envelopes        #
#    download at https://github.com/marcoalopez/Strength_envelopes/releases    #
#                                                                              #
#    Requirements:                                                             #
#        Python version 3.5 or higher                                          #
#        Numpy version 1.11 or higher                                          #
#        Matplotlib version 2.0 or higher                                      #
#                                                                              #
# ============================================================================ #

# Import required scientific libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.style.use('ggplot')  # you can use other plot styles as well

# ==============================================================================#
# DEFAULT INPUT PARAMETERS

"""Assumed constant values"""
# Miscellanea
g = 9.80665  # average gravitational acceleration [m/s**2]
R = 8.3144621  # universal gas constant [J mol**-1 K**-1]

# Mechanical
ro_crust = 2750  # average rock density in the crust [kg/m**3]
ro_mantle = 3330  # average rock density in the mantle [kg/m**3]
moho = 34.4  # Average continental crust thickness [km] (Huang et al. 2013)
lithosphere_base = 81  # Average lithosphere-asthenosphere boundary (LAB) [km] beneath tectonically altered regions (Rychert and Shearer, 2009)
ss_rate = 1.0e-14  # Reference average shear strain rate in the ductile lithosphere [s**-1]; see Twiss and Moores (2007, p.488)


# ==============================================================================#
# DO NOT MODIFY THE CODE BELOW - UNLESS YOU KNOW WHAT YOU'RE DOING!

# ==============================================================================#
# FUNCTIONS TO GENERATE STUFF IN THE DIFFERENTIAL STRENGTH VS DEPTH PLOT

def fric_strength(z, form='thrust', mu=0.73, lamb=0.36, C0=0.0, annot=None):
    """ Plot frictional slopes in the depth vs differential stress space.

    Parameters
    ----------
    z: integer or float
        maximum depth [km]

    form: string
        the type of fault, either 'thrust', 'normal' or 'strike'.

    mu: float between 0 an 1
        Coefficient of friction. Default value 0.73; this is the Rutter and Glover
        (2012) coefficient recalculated from Byerlee (1978) data.

    lamb: float between 0 and 1.
        Hubbert-Rubbey coefficient of fluid pressure. Default = 0.36

    annot: string
        automatically annotates fault 'type' or 'mu' and 'lambda' values in a legend.

    C0: integer or float
        Internal cohesion of the rock. Mostly negligible in nature. Default = 0.0
        This parameter can be used as the frictional cohesive strenght too.

    Assumptions
    -----------
    - Independency of rock type, temperature, and strain rate (Byerlee's law)

    - Dependency to pressure, pore fluid, and stress state (tension, compression,
    or shear)

    - The default value of coefficient of fluid pressure (0.36) is the result of
    dividing the water density by the average crust densitiy. This assumes that
    the water is free to flow throughout the upper crust (i.e. hydrostatic pressure)

    - The surface elevation is always set to zero and therefore the maximun depth
    is measured relative to the surface elevation not the mean sea level
    (Lagrangian reference frame)

    Calls function(s)
    -----------------
    Anderson_thrust; Anderson_extension; Anderson_strike
    """

    # Compute differential stress values depending on the type of fault
    if form == 'thrust':
        x = [Anderson_thrust(0, mu, C0, lamb),
             Anderson_thrust(z, mu, C0, lamb)]

    elif form == 'normal':
        x = [Anderson_extension(0, mu, C0, lamb),
             Anderson_extension(z, mu, C0, lamb)]

    elif form == 'strike':
        x = [Anderson_strike(0, mu, C0, lamb),
             Anderson_strike(z, mu, C0, lamb)]

    else:
        print("Wrong form. Please try again using 'thrust', 'normal' or 'strike'.")
        return None

    y = [0, z]

    if annot is not None:
        if annot == 'type':
            ax1.plot(x, y, label='{n}'.format(n=form))
            ax1.legend(fontsize=9)
            return None
        elif annot == 'lambda':
            ax1.plot(x, y, label=r'$\lambda$ = {n}'.format(n=lamb))
            ax1.legend(fontsize=9)
            return None
        elif annot == 'mu':
            ax1.plot(x, y, label=r'$\mu$ = {n}'.format(n=mu))
            ax1.legend(fontsize=9)
            return None

    return ax1.plot(x, y)


def quartz_dislocation_creep(z0, T_values, depth_values, form='Luan', ss_rate=1.0e-14, d=35, m=0.0):
    """ Plot flow law curves for dislocation creep in quartz in the differential stress
    vs depth space. Only post-1992 dislocation creep flow laws are considered.

    Parameters
    ----------
    z0: integer or float
        starting depth [km]

    T_values: array_like
        temperature variation with depth [K]

    depth_values: array_like
        acorresponding depths [km]

    form: string
        the flow law default parameters, either 'Luan', 'Gleason', 'Hirth',
        'Holyoke', or Rutter'. Default='Luan'

    ss_rate: float
        strain rate [s**-1]. Assumed average shear strain rate in the ductile
        lithosphere = 1.0e-14

    d: integer or float
        Grain size [microns]. Default value is 35. You can ignore this value as
        long as the grain size exponent [m] is equal to zero.

    m: integer or float.
        Grain size exponent. Default exponent is zero.

    Assumptions
    -----------
    - The effect of pressure is ignored since is relatively small at crustal
    depths.

    - The water fugacity is not well constrained for quartz flow laws,
    therefore the constant exponent is set to zero by default.

    - The effect of partial melt is not considered.

    Calls function(s)
    -----------------
    power_law_creep
    """

    if form == 'Luan':  # from Luan and Paterson (1992)
        n = 4.0  # stress exponent
        Q = 152000  # activation energy [J mol**-1]
        A = 10**(-7.2)  # material parameter [MPa**-n s**-1]

    elif form == 'Gleason':  # from Gleason and Tullis (1995). Wet quartzite.
        n = 4.0  # stress exponent
        Q = 223000  # activation energy [J mol**-1]
        A = 1.1e-4  # material parameter [MPa**-n s**-1]

    elif form == 'Holyoke':  # Gleason and Tullis (1995) corrected by Holyoke and Kronenberg (2010)
        n = 4.0  # stress exponent
        Q = 223000  # activation energy [J mol**-1]
        A = 5.1e-4  # material parameter [MPa**-n s**-1]

    elif form == 'Hirth':  # from Hirth et al. (2001)
        n = 4.0  # stress exponent
        Q = 135000  # activation energy [J mol**-1]
        A = 10**(-11.2)  # material parameter [MPa**-n s**-1]

    elif form == 'Rutter':  # from Rutter and Brodie (2004). Wet quartzite, minor grain boundary sliding inferred.
        n = 2.97  # stress exponent
        Q = 242000  # activation energy [J mol**-1]
        A = 10**(-4.93)  # material parameter [MPa**-n s**-1]

    else:
        print("Wrong form. Please try again using 'Gleason', 'Luan', 'Hirth' or 'Rutter'")

    # Select a specific range of temperature gradient according to depths z0 and moho
    mask = np.logical_and(depth_values >= z0, depth_values <= moho)
    T_masked = T_values[mask]

    # set some default values for dislocation creep quartz flow laws
    V = 0  # Activation volume per mol. Negligible at crustal depths.
    P = 0  # Pressure. Negligible at crustal depths.
    f = 0  # Fugacity of water. Not well constrained.
    r = 0  # Water fugacity constant exponent. Not well constrained.

    # estimate differential stress values
    diff_stress = power_law_creep(ss_rate, A, n, Q, R, T_masked, P, V, d, m, f, r)

    return ax1.plot(diff_stress, depth_values[mask])


def olivine_dislocation_creep(T_values, depth_values, form='Hirth', ss_rate=1.0e-14, d=1000, m=0.0, f=0.0, r=0.0):
    """ Plot flow law curves for dislocation creep in olivine or peridotite in
    the differential stress vs depth space.

    Parameters
    ----------
    T_values: array_like
        temperature variation with depth [K]

    depth_values: array_like
        corresponding depths [km]

    form: string
        the flow law default parameters, either 'Hirth', 'Hirth_dry', 'Karato',
        'Karato_dry', or 'Zimmerman'. Default='Hirth'

    ss_rate: float
        strain rate [s**-1]. Assumed average shear strain rate in the ductile
        lithosphere = 1.0e-14

    d: integer or float
        Grain size [microns]. Default value is 35. You can ignore this value as
        long as the grain size exponent [m] is equal to zero.

    m: integer or float
        Grain size exponent in microns. Default exponent is zero.

    Assumptions
    -----------
    - The effect of partial melt is not considered.

    Calls function(s)
    -----------------
    power_law_creep
    """

    if form == 'Hirth':  # from Hirth and Kohlstedt (2003). Wet Olivine
        n = 3.5  # stress exponent
        Q = 520000  # activation energy [J mol**-1]
        A = 10**(3.2)  # material parameter [MPa**-n s**-1]
        V = 2.2e-05  # activation volume per mol [m**3 mol**-1]

    elif form == 'Hirth_dry':  # from Hirth and Kohlstedt (2003). Dry Olivine
        n = 3.5  # stress exponent
        Q = 530000  # activation energy [J mol**-1]
        A = 10**(5.0)  # material parameter [MPa**-n s**-1]
        V = 1.8e-05  # activation volume per mol [m**3 mol**-1]

    elif form == 'Karato':  # from Karato and Jung (2003). Wet olivine
        n = 3.0  # stress exponent
        Q = 470000  # activation energy [J mol**-1]
        A = 10**(2.9)  # material parameter [MPa**-n s**-1]
        V = 2.4e-05  # activation volume per mol [m**3 mol**-1]

    elif form == 'Karato_dry':  # from Karato and Jung (2003). Dry olivine
        n = 3.0  # stress exponent
        Q = 510000  # activation energy [J mol**-1]
        A = 10**(6.1)  # material parameter [MPa**-n s**-1]
        V = 1.4e-05  # activation volume per mol [m**3 mol**-1]

    elif form == 'Zimmerman':  # from Zimmerman and Kohlstedt (2004). Dry peridotite
        n = 4.3  # stress exponent
        Q = 550000  # activation energy [J mol**-1]
        A = 10**(4.8)  # material parameter [MPa**-n s**-1]
        V = 0.0  # activation volume per mol [m**3 mol**-1]; not provided.

    else:
        print("Wrong form. Please try again using 'Hirth', 'Hirth_dry', 'Karato', 'Karato_dry', or 'Zimmerman'")

    # Select a specific range of temperature gradient according to depths moho and lithosphere_base
    mask = np.logical_and(depth_values >= moho, depth_values <= lithosphere_base)
    T_masked = T_values[mask]

    # create an array with the corresponding pressures TODO
    P_list = []
    for z in depth_values[mask]:
        ro = ((moho / z) * ro_crust) + (((z - moho) / z) * ro_mantle)
        P = ro * g * z
        P_list.append(P)
    P_array = np.array(P_list)

    # estimate differential stress values
    diff_stress = power_law_creep(ss_rate, A, n, Q, R, T_masked, P_array, V, d, m, f, r)

    return ax1.plot(diff_stress, depth_values[mask])


# ==============================================================================#
# FUNCTIONS TO GENERATE DIFFERENT... IN THE TEMPERATURE VS DEPTH PLOT


def triple_point(form='Holdoway'):
    """ Plot the Al2SiO5 triple point in the depth vs temperature space"""

    if form == 'Holdoway':
        T = 500
        depth = 380000 / (ro_crust * g)
        T_And_Sill = 602.85  # check this!

    elif form == 'Pattison':
        T = 550
        depth = 450000 / (ro_crust * g)
        T_And_Sill = 800  # check this!

    else:
        print("Wrong form. Please try again using 'Holdoway' or 'Pattison'")

    ax2.plot([154.85, T], [0, depth], 'k-')  # Ky-And line
    ax2.plot([T, T_And_Sill], [depth, 0], 'k-')  # And-Sill line
    ax2.plot([T, 696.85], [depth, moho], 'k-')  # Ky-Sill line
    ax2.annotate('And', xy=(375, 5))
    ax2.annotate('Sill', xy=(650, 15))

    return None


def stable_geotherm(LAB=81, T_surf=280.65, crust_params=(64.0, 0.4, 3.2), mantle_params=(34, 0.0, 3.35)):
    """ Estimate and plot a steady-state thermal gradient for the continental
    lithosphere considering a two-layer model (crust vs lithospheric mantle).
    It uses the Turcotte and Schubert (1982) model (see thermal_gradient_eq
    function). Thermal parameters taken from Jaupart & Mareschal (2007).

    Parameters
    ----------
    LAB: a positive integer or float.
        depth of Lithosphere-Asthenosphere boundary in km (default = 81 km)

    T_surf: integer or float
        temperature at surface [K]; default = 280.65; this is 7.5 [deg C]
        or 45.5 [fahrenheit] as measured in the KTB borehole.

    crust_params: tuple with three integer or float values
        thermal parameters within the crust (Jq, A, K).

            | Jq - Average heat flux in the continental crust [mW m**-2]
            | A -  Average rate of radiogenic heat production [microW m**-3]
            | K -  Coefficient of thermal conductivity [W m**-1 K**-1]

            Default thermal values for the crust (see Jaupart & Mareschal, 2007):
                | Jq = 64.0
                | A = 0.4
                | K = 3.2  # in granite (Clark, 1966)

    mantle_params: tuple with three integer or float values
        thermal parameters within the lithospheric mantle (Jq, A, K).

            Default thermal values for the lithospheric mantle:
                | Jq = 34
                | A = 0.0
                | K = 2.8  # in peridotite (Clark, 1966)

    Assumptions
    -----------
    - The whole crust has the same average thermal values (Jq, A, K). The
    same applies for the lithospheric mantle.

    - The model requires providing the depth of the lithosphere base.

    - The surface elevation is always set to zero and therefore the LAB depth
    is measured relative to the surface elevation not the mean sea level
    (Lagrangian reference frame)

    Returns
    -------
    Two numpy arrays. One containing the variation of temperature [K]
    with depth and other the corresponding depths [m].
    """

    # extract thermal parameters
    Jq_crust, A_crust, K_crust = crust_params
    Jq_mantle, A_mantle, K_mantle = mantle_params

    # Estimate average thermal gradients
    Tg_crust = Jq_crust / K_crust
    Tg_mantle = Jq_mantle / K_mantle

    # Generate a mesh of depth values [m]
    depth_values = np.linspace(0, LAB * 1000, 2**12)  # density of mesh = 2^12
    moho_m = moho * 1000

    # Estimate temperatures
    T_crust = thermal_gradient_eq(0, depth_values[depth_values <= moho_m], T_surf, Jq_crust, A_crust, K_crust)
    rf_new = depth_values[depth_values <= moho][-1]
    T_mantle = thermal_gradient_eq(rf_new, depth_values[depth_values > moho_m], T_crust[-1], Jq_mantle, A_mantle, K_mantle)
    T_values = np.hstack((T_crust, T_mantle))

    print(' ')
    print('According to this model, the expected T at the base of the lithosphere is',
          round(T_values[-1] - 273.15, 1), '[deg C]')
    print('The temperature gradient in the crust is',
          round(Tg_crust, 2), '[K km-1]')
    print('The temperature gradient in the lithosphere mantle is',
          round(Tg_mantle, 2), '[K km-1]')
    print(' ')

    # plot data in the temperature vs depth space (ax2) [C deg vs km]
    ax2.plot(T_values - 273.15, depth_values / 1000, '-', label='Geothermal gradient')

    return T_values, depth_values


def borehole_data(form='KTB', T_surf=280.65):
    """ Plot thermal gradients from superdeep borehole data and their projection
    down to the Moho.

    Parameters
    ----------
    form: The source data to plot, either 'KTB', 'Kola', or 'Gravberg'. A string.
    T_surf: Temperature at surface [K]; this is 7.5 [deg C] or 45.5 [fahrenheit]
            as measured in the KTB borehole.
    """

    T0 = T_surf - 273.15  # convert [K] to [deg C]

    if form == 'KTB':
        # Temperature gradient [K/km] (Emmermann and Lauterjung, 1997)
        T_KTB_grad = 27.5
        max_depth = 9.101  # [km]
        ax2.plot([T0, max_depth * T_KTB_grad + T0],
                 [0, max_depth], label='KTB borehole')
        ax2.plot([max_depth * T_KTB_grad + T0, moho * T_KTB_grad],
                 [max_depth, moho], '--')

    elif form == 'Kola':
        # Temperature gradient [K/km] (Smithson et al., 2000)
        T_Kola_Grad = 15.5
        max_depth = 12.262  # [km]
        ax2.plot([T0, max_depth * T_Kola_Grad + T0],
                 [0, max_depth], label='Kola borehole')
        ax2.plot([max_depth * T_Kola_Grad + T0, moho * T_Kola_Grad],
                 [max_depth, moho], '--')

    elif form == 'Gravberg':
        # Temperature gradient [K/km] (Lund and Zoback, 1999)
        T_Baltic_Grad = 16.1
        max_depth = 6.779  # [km]
        ax2.plot([T0, max_depth * T_Baltic_Grad + T0],
                 [0, max_depth], label='Gravberg-1 borehole')
        ax2.plot([max_depth * T_Baltic_Grad + T0, moho * T_Baltic_Grad],
                 [max_depth, moho], '--')

    else:
        print(' ')
        print("Wrong form. Please try again using 'KTB', 'Kola' or 'Gravberg'")

    return None


def granite_solidus():
    """ Plot the granite solidus line in the temperature vs depth space.
    Curve values taken from Johannes and Holtz (1996).
    """

    # convert pressures to depths
    depths_wet_Gr = ((P_list_wetGr * 1.0e6) / (ro_crust * g)) / 1000

    # Estimate melting temperature at the base of the moho according to
    # the following linear relation: T = (P + 9551.25) / 9.93
    P_moho = ((moho * 1000) * g * ro_crust) / 1.0e6
    T_solidus_moho = (P_moho + 9551.25) / 9.93

    # plot
    ax2.plot(T_list_wetGr, depths_wet_Gr, 'k--')
    ax2.plot([961.86, T_solidus_moho], [0.0, moho], 'k--')

    return None


def Goetze_line():
    """Plot the Goetze's criterion (Briegel & Goetze, 1978) in the differential
    stress vs deep space.

    Assumptions
    -----------
    - g does not vary with depth (constant)
    - Average density for the entire crust is 2750 kg/m**3
    - Average density for the lithospheric mantle is 3330 kg/m**3
    - Surface elevation equal to 0 km
    """
    # convert km to meters
    z_moho = moho * 1000
    z_lithos = lithosphere_base * 1000

    # Depths [in km]
    depths = [0, moho, lithosphere_base]

    # Estimate the pressures [in MPa] at the corresponding depths
    moho_P = (ro_crust * g * z_moho) / 1e6
    ro = ((z_moho / z_lithos) * ro_crust) + (((z_lithos - z_moho) / z_lithos) * ro_mantle)
    lithos_base_P = (ro * g * z_lithos) / 1e6
    lithos_P = [0, moho_P, lithos_base_P]

    return ax1.plot(lithos_P, depths, 'k--', label="Goetze's criterion'")


# ==============================================================================#
# AUXILIARY FUNCTIONS (i.e. functions performing simple tasks using by the functions
# creating the plots


def Anderson_thrust(depth, mu, C0, lamb):
    """ Returns the corresponding differential stress in MPa for a specific depth
    in thrust faults using the Anderson theory of faulting (Anderson, 1905).

    Parameters
    ----------
    depth: the depth [km]
    mu: coefficient of friction
    C0: internal cohesion of the rock [MPa]
    lamb: coefficient of fluid pressure
    """
    depth = 1000 * depth  # convert km to m
    diff_stress = (2 * (C0 + mu * ro_crust * g * depth * (1 - lamb))) / (np.sqrt(mu**2 + 1) - mu)

    return diff_stress / 10**6


def Anderson_extension(depth, mu, C0, lamb):
    """ Returns the corresponding differential stress in MPa for a specific depth
    in normal faults using the Anderson theory of faulting (Anderson, 1905).

    Parameters
    ----------
    depth: the depth [km]
    mu: coefficient of friction
    C0: internal cohesion of the rock [MPa]
    lamb: coefficient of fluid pressure
    """
    depth = 1000 * depth  # convert km to m
    diff_stress = (- 2 * (C0 - mu * ro_crust * g * depth * (1 - lamb))) / (np.sqrt(mu**2 + 1) + mu)

    return diff_stress / 10**6


def Anderson_strike(depth, mu, C0, lamb):
    """ Returns the corresponding differential stress in MPa for a specific depth
    in strike-slip faults using the Anderson theory of faulting (Anderson, 1905).

    Parameters
    ----------
    depth: the depth [km]
    mu: coefficient of friction
    C0: internal cohesion of the rock [MPa]
    lamb: coefficient of fluid pressure
    """
    depth = 1000 * depth  # convert km to m
    diff_stress = (2 * (C0 + mu * ro_crust * g * depth * (1 - lamb))) / (np.sqrt(mu**2 + 1))

    return diff_stress / 10**6


def power_law_creep(ss_rate, A, n, Q, R, T, P, V, d, m, f, r):
    """ Return the neccesary differential stress (Tresca criterion) in MPa
    for permanently deforming a polycrystalline material at a given strain rate.

    Parameters
    ----------
    ss_rate: strain rate [s**-1]
    A: material constant [MPa**-n s**-1]
    n: stress exponent
    Q: activation energy [J mol**-1]
    R: universal gas constant [J mol**-1 K**-1]
    T: absolute temperature [K]
    P: pressure [MPa]
    V: activation volume per mol [m**3 mol**-1]
    d: mean grain size [microns]
    m: grain size exponent
    f: fugacity of water [water molecules per 1e6 Si atoms]
    r: water fugacity exponent

    Assumptions
    -----------
    - Steady-state creep
    - Moderate stress regime (roughly between 20 - 200 MPa)
    - Effect of partial melt not considered
    """

    return (ss_rate * (d**m) * (f**r) * np.exp((Q + P * V) / (R * T)) / A)**(1 / n)


def thermal_gradient_eq(z0, z, T_surf, Jq, A, K):
    """ Apply the equation (model) of Turcotte and Schubert (1982) to estimate a
    steady-state geotherm (i.e. the T at a given depth).

    Parameters
    ----------
    z0: surface elevation [m]
    z: depth at the base of the model [m]
    T_surf: temperature on the Earth surface [K]
    Jq: average heat flux [mW m**-2]
    A: average heat productivity [microW m**-3]
    K: coefficient of thermal conductivity [W m**-1 K**-1]

    Assumptions
    -----------
    TODO

    Returns
    -------
    The temperature in K, a float
    """

    return T_surf + ((Jq / K) * (z - z0)) - ((A / (2 * K)) * (z - z0)**2)


def quartz_piezometer(d, form='Stipp'):
    """ Apply different quartz paleopieometric relations to estimate differential
    stress from 1D apparent grain sizes. The piezometric relations has the
    following expression:

    diff_stress = B d**-p

    where diff_stress is the differential stress in [MPa], B is an experimentally
    derived parameter in [MPa micron**p], d is the grain size in [microns], and p
    is an experimentally derived exponent which is adimensonal.

    Parameters
    ----------
    d: integer or float
        the apparent grain size in microns

    form: a string
        the piezometric relation to be used, either:
            | 'Cross' and 'Cross2' from Cross et al. (2017)
            | 'Holyoke' from Holyoke and Kronenberg (2010)
            | 'Shimizu' from Shimizu (2008)
            | 'Stipp' from Stipp and Tullis (2003)
            | 'Twiss' from Twiss (1977)

    References
    ----------
    TODO

    Assumptions
    -----------
    - Independence of temperature (excepting Shimizu's piezometer), total strain,
    flow stress, and water content.

    - The piezometer relations of Stipp and Tullis (2003), Holyoke and Kronenberg (2010),
    and Cross et al. (2007) requires to enter the grain size as the root mean square
    apparent grain size calculated from equivalent circular diameters with no stereological
    correction.

    - The piezometer relation of Shimizu (2009) requires to enter the ...abs
    apparent grain size calculated from equivalent circular diameters with no
    stereological correction.

    - The piezometer of Twiss (1977) requires to enter the mean apparent grain size
    calculated from equivalent circular diameters with no stereological correction.
    The function will convert this value to the mean linear intercept grain size
    according to de Hoff and Rhines (1968) empirical relation...TODO

    TODO

    Returns
    -------
    The differential stress in MPa, a float"""

    if form == 'Stipp':
        B = 669.0
        p = 0.79

    elif form == 'Holyoke':
        B = 490.3
        p = 0.79

    elif form == 'Cross':
        B = 593.0
        p = 0.71

    elif form == 'Cross2':
        B = 450.9
        p = 0.63

    elif form == 'Shimizu':
        B = 349.9
        p = 0.8
        pass

    elif form == 'Twiss':
        B = 603.1  # Recalculated from Twiss (1977) using [5.5 * (1000**0.68)] (Note: B is 5.5 when grain size (d) is in mm)
        p = 0.68
        d = d / (np.sqrt(4 / np.pi))  # convert equivalent circular diameter to linear intercept (de Hoff and Rhines, 1968)

    else:
        print('Wrong from. Please choose between valid forms')
        return None

    return B * d**-p

# ==============================================================================#


T_list_wetGr = np.array([632.203, 635.593, 640.254, 644.915, 647.034, 649.186, 652.128, 655.561, 660.220, 665.860, 671.010, 676.895,
                         684.251, 692.589, 700.190, 709.999, 719.072, 730.106, 744.329, 757.815, 778.413, 797.295, 815.686, 856.391, 906.415, 961.86])
P_list_wetGr = np.array([1297.289, 1040.060, 787.048, 546.687, 468.675, 417.936, 371.570, 332.525, 294.700, 260.535, 234.912,
                         210.509, 186.106, 162.923, 144.620, 122.657, 105.575, 87.273, 68.970, 56.769, 45.177, 37.856, 32.366, 25.045, 18.334, 0.00])

texto = """
#======================================================================================#
#                                                                                      #
#                      Welcome to Strength envelopes script v0.1                       #
#                                                                                      #
#  The following methods are available:                                                #
#                                                                                      #
#  DIFFERENTIAL STRESS vs DEPTH plot                                                   #
#                                                                                      #
#      fric_strength  # plot friccional slopes                                         #
#      quartz_dislocation_creep  # plot flow laws for dislocation creep in quartz      #
#      olivine_dislocation_creep  # plot flow laws for dislocation creep in olivine    #
#      Goetze_line  # plot the Goetze criterion                                        #
#                                                                                      #
#  TEMPERATURE vs DEPTH plot                                                           #
#                                                                                      #
#      triple_point  # plot the Al2SiO5 triple point                                   #
#      granite_solidus  # plot the granite solidus line for wet and dry...             #
#      borehole_data  # plot temperature gradients from superdeep boreholes            #
#      stable_geotherm  # estimate a stable geotherm based on...TODO                   #
#                                                                                      #
#  You can get information on the different methods by:                                #
#                                                                                      #
#  (1) typing help(name of the method) in the console. e.g. >>> help(stable_geotherm)  #
#                                                                                      #
#  (2) in the Spyder console by writing the name of the method and clicking Ctrl + I   #
#                                                                                      #
#  (3) Visit the documentation webpage at http://...TODO                               #
#                                                                                      #
#======================================================================================#
"""

print(' ')
print(texto)

# Initialize the figure base

fig = plt.figure(tight_layout=True)

ax1 = fig.add_subplot(121)
plt.gca().invert_yaxis()
plt.gca().xaxis.tick_top()
plt.gca().xaxis.set_label_position('top')
ax1.set_xlabel('Differential stress (MPa)')
ax1.set_ylabel('Depth (km)')
ax1.plot([0, 600], [moho, moho], 'k-')
ax1.text(0, moho - moho / 90, 'Average Moho', fontsize=10)
ax1.plot(0, 0)

ax2 = fig.add_subplot(122)
plt.gca().invert_yaxis()
plt.gca().xaxis.tick_top()
plt.gca().xaxis.set_label_position('top')
ax2.set_xlabel('Temperature ($\degree C$)')
ax2.plot([0, 1100], [moho, moho], 'k-')
ax2.text(0, moho - moho / 90, 'Average Moho', fontsize=10)
ax2.plot([0, 1100], [lithosphere_base, lithosphere_base], 'k-')
ax2.text(0, lithosphere_base - lithosphere_base / 90, 'lithosphere base', fontsize=10)

triple_point(form='Holdoway')
granite_solidus()

plt.show()
