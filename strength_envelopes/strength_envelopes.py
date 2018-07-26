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
from scipy.constants import g, R
from flow_laws import olivine, quartz
import thermal_functions as tf
import mechanical_functions as mf

# ==============================================================================#
# DEFAULT INPUT PARAMETERS

# Mechanical constants (CAUTION! these are global variables and thus changing their values will affect the results of different functions)
ro_crust = 2750  # average rock density in the crust [kg/m**3]
ro_mantle = 3330  # average rock density in the mantle [kg/m**3]
ref_sr = 1.0e-14  # Reference average shear strain rate in the ductile lithosphere [s**-1]; see Twiss and Moores (2007, p.488)
moho = 34.4  # Average continental crust thickness [km] (Huang et al. 2013)
LAB = 81  # Average lithosphere-asthenosphere boundary (LAB) [km] beneath tectonically altered regions (Rychert and Shearer, 2009)

# set plot style
plot_style = 'ggplot'
mpl.style.use(plot_style)
# you can use other styles as well, see the following gallery:
# https://tonysyu.github.io/raw_content/matplotlib-style-gallery/gallery.html
# ==============================================================================#
# DO NOT MODIFY THE CODE BELOW - UNLESS YOU KNOW WHAT YOU'RE DOING!

ax1 = None
ax2 = None
ax = None


def fric_strength(z, fault_type='strike-slip', mu=0.73, lamb=0.36, C0=0.0, annot=None, **kwargs):
    """ Estimate and plot frictional strength slopes in the depth vs differential stress space.

    Parameters
    ----------
    z : scalar
        maximum depth [km].

    fault_type : string
        the type of fault, either 'inverse', 'normal' or 'strike-slip'.

    mu : scalar between 0 an 1, optional
        Coefficient of friction. Default value 0.73; this is the Rutter and Glover
        (2012) coefficient recalculated from Byerlee (1978) data.

    lamb : scalar between 0 and 1, optional
        Hubbert-Rubbey coefficient of fluid pressure. Zero is for dry conditions.
        Default = 0.36

    C0 : scalar, optional
        Internal cohesion of the rock. Mostly negligible in nature. Default = 0.0
        This parameter can be used as the frictional cohesive strenght as well.

    annot : None or string, optional
        automatically annotates fault 'type' or 'mu' and 'lambda' values in a legend.

    kwargs : `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls),
        norm, cmap, transform, etc.

    Assumptions
    -----------
    - Independency of rock type, temperature, and strain rate (Byerlee's law)

    - Dependency to pressure, pore fluid, and stress state (tension, compression,
    or shear)

    - The default value of coefficient of fluid pressure (0.36) is the result of
    dividing the water density by the average crust densitiy. This assumes that
    the water is free to flow throughout the upper crust (i.e. hydrostatic pressure)

    - The surface elevation is always set to zero and thus the maximun depth
    is measured relative to the surface elevation not the mean sea level
    (Lagrangian reference frame)

    Examples
    --------
    fric_strength(z=15, fault='normal')
    fric_strength(z=20, fault='inverse', annot='lamb', lamb=0.5)
    fric_strength(z=15, color='red', linewidth=3)

    Calls functions
    -----------------
    Anderson_thrust; Anderson_extension; Anderson_strike
    """

    # Compute differential stress values depending on the type of fault
    if fault_type == 'strike-slip':
        x = [mf.Anderson_fault('strike', 0, mu, C0, lamb, ro_crust),
             mf.Anderson_fault('strike', z, mu, C0, lamb, ro_crust)]

    elif fault_type == 'inverse':
        x = [mf.Anderson_fault('thrust', 0, mu, C0, lamb, ro_crust),
             mf.Anderson_fault('thrust', z, mu, C0, lamb, ro_crust)]

    elif fault_type == 'normal':
        x = [mf.Anderson_fault('extension', 0, mu, C0, lamb, ro_crust),
             mf.Anderson_fault('extension', z, mu, C0, lamb, ro_crust)]

    else:
        raise ValueError("Faul type misspelled. Please use 'inverse', 'normal' or 'strike-slip'.")

    y = [0, z]

    print('')
    print('fault type:', fault_type)
    print('Coefficient of friction =', mu)
    print('Coefficient of fluid pressure =', lamb)
    print('Internal cohesion (or frictional cohesive strength) =', C0)
    print(' ')

    if annot is not None:
        if annot == 'type':
            ax1.plot(x, y, label='{n}'.format(n=fault_type))
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

    return ax1.plot(x, y, **kwargs)


def stable_geotherm(T_surf=280.65, crust_params=(65, 0.97, 2.51),
                    mantle_params=(34, 0.01, 3.35), **kwargs):
    """ Estimate and plot a steady-state thermal gradient for the continental
    lithosphere considering a two-layer model (crust vs lithospheric mantle).
    It uses the Turcotte and Schubert (1982) model (see thermal_gradient_eq
    function).

    Parameters
    ----------
    T_surf : positive scalar, optional
        temperature at surface [K]; default = 280.65; this is 7.5 [deg C]
        or 45.5 [fahrenheit] as measured in the KTB borehole.

    crust_params : tuple with three scalar values, optional
            | Jq - Average heat flux in the continental crust [mW m**-2]
            | A -  Average rate of radiogenic heat production [microW m**-3]
            | K -  Coefficient of thermal conductivity [W m**-1 K**-1]

            Default thermal values for the crust:
                | Jq = 65  # from Jaupart and Mareschal (2007)
                | A = 0.97  # average crust from Huang et al. (2013)
                | K = 2.51  # average crust from Sclater et al. (1980)

    mantle_params : tuple with three scalar values, optional
        thermal parameters within the lithospheric mantle (Jq, A, K).

            Default thermal values for the lithospheric mantle:
                | Jq = 34  # from Sclater et al. (1980)
                | A = 0.01  # from Sclater et al. (1980)
                | K = 3.35  # in peridotite at room T (Sclater et al., 1980)

    kwargs : `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls),
        norm, cmap, transform, etc.

    Assumptions
    -----------
    - The same average thermal values (Jq, A, K) apply for whole crust and
    the lithospheric mantle.
    - The model requires providing the depth of the lithosphere base (LAB).
    - The surface elevation is always set to zero and hence the LAB depth
    is measured relative to the surface elevation not the mean sea level
    (Lagrangian reference frame).
    - The thermal properities of the rocks are considered +-isotropic.
    - The temperature dependence of thermal conductivity is neglected.

    Examples
    --------
    my_model = stable_geotherm()
    another_model = stable_geotherm(crust_params=(75, 0.97, 2.51), color='orange')

    Call function
    -------------
    thermal_gradient_eq

    Returns
    -------
    Two 1D numpy arrays. One containing the variation of temperature [K]
    with depth and other with the corresponding depths [m].
    """

    # extract thermal parameters
    Jq_crust, A_crust, K_crust = crust_params
    Jq_mantle, A_mantle, K_mantle = mantle_params

    # Estimate average thermal gradients
    Tg_crust = Jq_crust / K_crust
    Tg_mantle = Jq_mantle / K_mantle

    # Generate a mesh of depth values [km]
    depth_values = np.linspace(0, LAB, 2**12)  # mesh density = 2^12

    # Estimate stable geotherm
    T_crust = tf.turcotte_schubert_eq(0, depth_values[depth_values <= moho], T_surf, Jq_crust, A_crust, K_crust)
    new_ref_frame = depth_values[depth_values <= moho][-1]
    T_mantle = tf.turcotte_schubert_eq(new_ref_frame, depth_values[depth_values > moho], T_crust[-1], Jq_mantle, A_mantle, K_mantle)
    T_values = np.hstack((T_crust, T_mantle))

    T_at_moho_index = int(np.argwhere(depth_values <= moho)[-1])
    T_at_moho = T_values[T_at_moho_index] - 273.15

    print(' ')
    print('ACCORDING TO THE MODEL:')
    print('The T at the base of the moho is {val} [deg C]' .format(val=round(T_at_moho, 1)))
    print('The T at the lithosphere-asthenosphere boundary is {val} [deg C]' .format(val=round(T_values[-1] - 273.15, 1)))
    print('The average temperature gradient in the crust is {val} [K km-1]' .format(val=round(Tg_crust, 2)))
    print('The average temperature gradient in the lithospheric mantle is {val} [K km-1]' .format(val=round(Tg_mantle, 2)))

    # plot data in the temperature vs depth space (ax2) [C deg vs km]
    ax2.plot(T_values - 273.15, depth_values, '-', label='Geothermal gradient', **kwargs)

    return T_values, depth_values


def qtz_disloc_creep(z0, geotherm, flow_law='HTD', strain_rate=ref_sr, d=35, m=0.0, fug=0.0, r=0.0, **kwargs):
    """ Plot flow law curves for dislocation creep in quartz in the differential stress
    vs depth space. Only post-1992 dislocation creep flow laws are considered.

    Parameters
    ----------
    z0 : scalar
        starting depth [km]

    geotherm : array_like (2-dimensional)
        temperature variation with depth [K] and corresponding depths [km]

    flow_law : string, optional, default: 'HTD'
        the flow law used, either 'HTD', 'LP_wet', 'GT_wet',
        'HK_wet', or 'RB_wet'.

    strain_rate : scalar, optional
        strain rate [s**-1]. Assumed average shear strain rate in the ductile
        lithosphere = 1.0e-14

    d : scalar, optional, default: 35
        Grain size [microns]. You can ignore this value as long as the grain
        size exponent [m] is equal to zero.

    m : scalar, optional, default: 0
        Grain size exponent.

    fug : scalar, optional, default: 0
        Water fugacity.

    r : scalar, optional, default: 0
        Water fugacity constant exponent.

    kwargs : `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls),
        norm, cmap, transform, etc.

    Assumptions
    -----------
    - The effect of pressure is ignored at crustal depths.
    - The water fugacity is not well constrained for quartz flow laws. Hence the
    constant exponent and the water fugacity are both set to zero by default.
    - The effect of partial melt is ignored.

    Examples
    --------
    qtz_disloc_creep(z0=9, geotherm=my_model, color='red', linewidth=3)
    qtz_disloc_creep(z0=10, geotherm=my_model, flow_law='GT_wet', strain_rate=5.0e-14)

    Calls function(s)
    -----------------
    power_law_creep
    """

    # extract temperature gradient and depths
    T_gradient, depths = geotherm

    # extract experimentally derived values for dislocation creep quartz flow law
    n, Q, A = quartz(flow_law)

    # fix some values for dislocation creep quartz flow laws
    V = 0  # Activation volume per mol. Negligible at crustal depths.
    P = 0  # Pressure. Negligible at crustal depths.

    # Select a specific range of temperature gradient according to depths z0 and moho
    mask = np.logical_and(depths >= z0, depths <= moho)
    T_masked = T_gradient[mask]

    # estimate differential stress values
    diff_stress = mf.power_law_creep(strain_rate, A, n, Q, R, T_masked, P, V, d, m, fug, r)

    return ax1.plot(diff_stress, depths[mask], **kwargs)


def ol_disloc_creep(geotherm, flow_law='HK_dry', strain_rate=ref_sr, d=1000, m=0.0, fug=0.0, r=0.0, **kwargs):
    """ Plot flow law curves for dislocation creep in olivine or peridotite in
    the differential stress vs depth space.

    Parameters
    ----------
    geotherm : array_like (2-dimensional)
        temperature variation wth depth [K] and corresponding depths [km]

    flow_law : string, optional
        the flow law default parameters, either 'HK_wet', 'HK_dry', 'KJ_wet',
        'KJ_dry', 'ZK_dry', 'Faul_dry'. Default='HK_dry'

    strain_rate : scalar, optional
        strain rate [s**-1]. Assumed average shear strain rate in the ductile
        lithosphere = 1.0e-14

    d : scalar, optional
        Grain size [microns]. Default value is 1 mm. You can ignore this value as
        long as the grain size exponent [m] is equal to zero.

    m : scalar, optional
        Grain size exponent in microns. Default exponent is zero.

    fug : scalar, optional
        Fugacity of water.

    r : scalar, optional
        Water fugacity constant exponent.

    kwargs: `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls),
        norm, cmap, transform, etc.

    Assumptions
    -----------
    - The effect of partial melt is ignored.
    - Olivine dislocation creep only applies below the moho

    Examples
    --------
    ol_disloc_creep(geotherm=my_model, flow_law='Faul_dry')
    ol_disloc_creep(geotherm=my_model, fug=..., r=...)

    Calls function(s)
    -----------------
    get_olivine_values
    power_law_creep
    """

    # extract temperature gradient and depths
    T_gradient, depths = geotherm

    # extract experimentally derived values for dislcation creep olivine flow law
    n, Q, A, V, r = olivine(flow_law)

    # Select a specific range of temperature gradient according to moho and
    # LAB depths
    mask = np.logical_and(depths >= moho, depths <= LAB)
    T_masked = T_gradient[mask]

    # create a list with the corresponding pressures
    P_list = []  # preallocate this list if length is usually larger than 1e6! TODO
    for z in depths[mask]:
        ro = ((moho / z) * ro_crust) + (((z - moho) / z) * ro_mantle)
        P = ro * g * z
        P_list.append(P)
    P_array = np.array(P_list)

    # estimate differential stress values
    diff_stress = mf.power_law_creep(strain_rate, A, n, Q, R, T_masked, P_array, V, d, m, fug, r)

    return ax1.plot(diff_stress, depths[mask], **kwargs)


# ==============================================================================#
# OTHER FUNCTIONS


def triple_point(t_point='Holdoway'):
    """ Plot the Al2SiO5 triple point in the depth vs temperature space"""

    if t_point == 'Holdoway':
        T = 500
        depth = 380000 / (ro_crust * g)
        T_And_Sill = 602.85  # check this!

    elif t_point == 'Pattison':
        T = 550
        depth = 450000 / (ro_crust * g)
        T_And_Sill = 800  # check this!

    else:
        raise ValueError("Triple point misspelled. Use 'Holdoway' or 'Pattison'")

    ax2.plot([154.85, T], [0, depth], 'k-')  # Ky-And line
    ax2.plot([T, T_And_Sill], [depth, 0], 'k-')  # And-Sill line
    ax2.plot([T, 696.85], [depth, moho], 'k-')  # Ky-Sill line
    ax2.annotate('And', xy=(375, 5))
#    ax2.annotate('Sill', xy=(650, 15))

    return None


def borehole_data(borehole='KTB', T_surf=280.65):
    """ Plot thermal gradients from superdeep boreholes and project them down
    to the Moho discotinuity.

    Parameters
    ----------
    borehole : string, optional
        Name of the borehole data, either 'KTB' (default), 'Kola', or 'Gravberg'

    T_surf : positive scalar, optional
        Temperature at surface [K]. Default: 7.5 [deg C] or 45.5 [fahrenheit]
        as measured in the KTB borehole.
    """

    T0 = T_surf - 273.15  # convert [K] to [deg C]

    if borehole == 'KTB':
        # Temperature gradient [K/km] (Emmermann and Lauterjung, 1997)
        T_KTB_grad = 27.5
        max_depth = 9.101  # [km]
        ax2.plot([T0, max_depth * T_KTB_grad + T0],
                 [0, max_depth], label='KTB borehole')
        ax2.plot([max_depth * T_KTB_grad + T0, moho * T_KTB_grad],
                 [max_depth, moho], '--')

    elif borehole == 'Kola':
        # Temperature gradient [K/km] (Smithson et al., 2000)
        T_Kola_Grad = 15.5
        max_depth = 12.262  # [km]
        ax2.plot([T0, max_depth * T_Kola_Grad + T0],
                 [0, max_depth], label='Kola borehole')
        ax2.plot([max_depth * T_Kola_Grad + T0, moho * T_Kola_Grad],
                 [max_depth, moho], '--')

    elif borehole == 'Gravberg':
        # Temperature gradient [K/km] (Lund and Zoback, 1999)
        T_Baltic_Grad = 16.1
        max_depth = 6.779  # [km]
        ax2.plot([T0, max_depth * T_Baltic_Grad + T0],
                 [0, max_depth], label='Gravberg-1 borehole')
        ax2.plot([max_depth * T_Baltic_Grad + T0, moho * T_Baltic_Grad],
                 [max_depth, moho], '--')

    else:
        print(' ')
        raise ValueError("Borehole name misspelled. Use 'KTB', 'Kola' or 'Gravberg'")

    return None


def granite_solidus(**kwargs):
    """ Plot the granite solidus line in the temperature vs depth space.
    P-T values from Johannes and Holtz (1996).

    Parameters
    ----------
    kwargs : `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls),
        norm, cmap, transform, etc.
    """

    # convert pressures to depths
    depths_wet_Gr = ((P_list_wetGr * 1.0e6) / (ro_crust * g)) / 1000

    # Estimate melting temperature at the base of the moho according to
    # the following linear relation: T = (P + 9551.25) / 9.93
    P_moho = ((moho * 1000) * g * ro_crust) / 1.0e6
    T_solidus_moho = (P_moho + 9551.25) / 9.93

    # plot
    ax2.plot(T_list_wetGr, depths_wet_Gr, 'k--', **kwargs)
    ax2.plot([961.86, T_solidus_moho], [0.0, moho], 'k--', **kwargs)

    print('')
    print('values from Johannes and Holtz (1996)')

    return None


def peridotite_solidus(**kwargs):
    """ Plot the peridotite solidus line in the temperature vs depth space.
    P-T values from TODO (xxxx).

    Parameters
    ----------
    kwargs : `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls),
        norm, cmap, transform, etc.
    """

#    TODO

    pass


def goetze_line(**kwargs):
    """Plot the Goetze's criterion (Briegel & Goetze, 1978) in the differential
    stress vs deep space.

    Parameters
    ----------
    kwargs : `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls),
        norm, cmap, transform, etc.

    Assumptions
    -----------
    - g does not vary with depth (constant value)
    - Average density for the entire crust is 2750 kg/m**3
    - Average density for the lithospheric mantle is 3330 kg/m**3
    - Surface elevation set to 0 km

    Future implementations
    ----------------------
    Use the PREM model - TODO
    """
    # convert km to meters
    z_moho = moho * 1000
    z_lithos = LAB * 1000

    # Depths [in km]
    depths = [0, moho, LAB]

    # Estimate the pressures [in MPa] at the corresponding depths
    moho_P = (ro_crust * g * z_moho) / 1e6
    ro = ((z_moho / z_lithos) * ro_crust) + (((z_lithos - z_moho) / z_lithos) * ro_mantle)
    lithos_base_P = (ro * g * z_lithos) / 1e6
    lithos_P = [0, moho_P, lithos_base_P]

    # ax1.fill_between()

    return ax1.plot(lithos_P, depths, 'k--', label="Goetze's criterion'", **kwargs)


# ==============================================================================#


def init_plot(double_plot=True):
    """ Initialize the figure base.

    Parameters
    ----------
    moho : positive scalar
        the depth of the moho in km

    LAB : positive scalar
        the depth of the lithosphere-asthenosphere boundary (LAB)

    double_plot : boolean
        If True, two plots will appear: a diff. stress vs depth and a T vs depth.
        If False only a differential stress vs depth plot will be plotted.

    Examples
    --------
    >>> fig (ax1, ax2) = init_plot()
    >>> fig, ax1 = init_plot(doble_plot=False)

    Important note: for a correct use of the script you must use ax1 and ax2
    as the name of the figure axes

    Return
    ------
    the figure and axes matplotlib objects
    """
    if double_plot is True:
        fig = plt.figure()

        ax1 = fig.add_subplot(121)
        plt.gca().invert_yaxis()
        plt.gca().xaxis.tick_top()
        plt.gca().xaxis.set_label_position('top')
        ax1.set(xlabel='Differential stress (MPa)', ylabel='Depth (km)')
        ax1.plot([0, 600], [moho, moho], 'k-')
        ax1.text(0, moho - moho / 90, 'Moho', fontsize=10)
        ax1.plot([0, 600], [LAB, LAB], 'k-')
        ax1.text(0, LAB - LAB / 90, 'lithosphere base', fontsize=10)
        ax1.plot(0, 0)

        ax2 = fig.add_subplot(122)
        plt.gca().invert_yaxis()
        plt.gca().xaxis.tick_top()
        plt.gca().xaxis.set_label_position('top')
        ax2.set(xlabel='Temperature ($\degree C$)')
        ax2.plot([0, 1300], [moho, moho], 'k-')
        ax2.text(0, moho - moho / 90, 'Moho', fontsize=10)
        ax2.plot([0, 1300], [LAB, LAB], 'k-')
        ax2.text(0, LAB - LAB / 90, 'lithosphere base', fontsize=10)
        ax2.plot(0, 0, 'k+')

        fig.tight_layout()

        return fig, (ax1, ax2)

    else:
        fig, ax = plt.subplots()

        plt.gca().invert_yaxis()
        plt.gca().xaxis.tick_top()
        plt.gca().xaxis.set_label_position('top')
        ax.set(xlabel='Differential stress (MPa)', ylabel='Depth (km)')
        ax.plot([0, 600], [moho, moho], 'k-')
        ax.text(0, moho - moho / 90, 'Moho', fontsize=10)
        ax.plot([0, 600], [LAB, LAB], 'k-')
        ax.text(0, LAB - LAB / 90, 'lithosphere base', fontsize=10)
        ax.plot(0, 0)

        fig.tight_layout()

        return fig, ax


T_list_wetGr = np.array([632.203, 635.593, 640.254, 644.915, 647.034, 649.186, 652.128, 655.561, 660.220, 665.860, 671.010, 676.895,
                         684.251, 692.589, 700.190, 709.999, 719.072, 730.106, 744.329, 757.815, 778.413, 797.295, 815.686, 856.391, 906.415, 961.86])
P_list_wetGr = np.array([1297.289, 1040.060, 787.048, 546.687, 468.675, 417.936, 371.570, 332.525, 294.700, 260.535, 234.912,
                         210.509, 186.106, 162.923, 144.620, 122.657, 105.575, 87.273, 68.970, 56.769, 45.177, 37.856, 32.366, 25.045, 18.334, 0.00])


texto = """
======================================================================================
Welcome to Strength envelopes script v1.0
======================================================================================

Strength envelopes is a free open-source cross-platform script to generate strength
envelopes.

METHODS AVAILABLE
====================  ================================================================
Main Functions        Description
====================  ================================================================
fric_strength         Plot frictional slopes
stable_geotherm       Estimate and plot a steady-state geothermal gradient
qtz_disloc_creep      Plot dislocation creep flow laws for quartz
ol_disloc_creep       Plot dislocation creep flow laws for olivine

======================  ==============================================================
Other functions
====================  ================================================================
triple_point          Plot the Al2SiO5 triple point (Holdoway or Pattison)
goetze_line           Plot the Goetze criterion
granite_solidus       Plot granite solidus (wet and dry)
peridotite_solidus    Plot peridotite solidus NOT YET IMPLEMENTED!
borehole_data         Plot temperature gradients from superdeep boreholes
====================  ================================================================

You can get information on the different methods by:
    (1) Typing the command help in the console as follows: help(name of the function)
        e.g. >>> help(stable_geotherm)
    (2) In the Spyder IDE by writing the name of the function and clicking Ctrl+I
    (3) Visit script documentation at https://github.com/marcoalopez/Strength_envelopes


EXAMPLES
--------
Initialize a figure
fig, (ax1, ax2) = init_plot()

For more examples see documentation or use help(function_name)
"""

print(' ')
print(texto)