import os , cv2
import numpy as np
import pandas as pd
from collections import Counter
from scipy import stats
from plotnine import ggplot, aes, geom_line, scale_x_continuous, scale_color_manual
from plantcv.plantcv import fatal_error
from plantcv.plantcv import params
from plantcv.plantcv import outputs


def analyze_color(rgb_img, mask, bins, hist_plot_type=None):
    """Analyze the color properties of an image object
    Inputs:
    rgb_img          = RGB image data
    mask             = Binary mask made from selected contours
    bins             = number of color bins the channel is divided into
    hist_plot_type   = 'None', 'all', 'rgb','lab' or 'hsv'
    
    Returns:
    color_header     = color histogram data table headers
    color_data       = color histogram data table values
    analysis_image   = histogram output
    
    :param rgb_img: numpy.ndarray
    :param mask: numpy.ndarray
    :param bins: int
    :param hist_plot_type: str
    :return color_header: list
    :return color_data: list
    :return analysis_images: list
    """

    params.device += 1

    if len(np.shape(rgb_img)) < 3:
        fatal_error("rgb_img must be an RGB image")

    masked = cv2.bitwise_and(rgb_img, rgb_img, mask=mask)
    b, g, r = cv2.split(masked)
    lab = cv2.cvtColor(masked, cv2.COLOR_BGR2LAB)
    l, m, y = cv2.split(lab)
    hsv = cv2.cvtColor(masked, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Color channel dictionary
    norm_channels = {"b": np.divide(b, (256 / bins)).astype(np.uint8),
                     "g": np.divide(g, (256 / bins)).astype(np.uint8),
                     "r": np.divide(r, (256 / bins)).astype(np.uint8),
                     "l": np.divide(l, (256 / bins)).astype(np.uint8),
                     "m": np.divide(m, (256 / bins)).astype(np.uint8),
                     "y": np.divide(y, (256 / bins)).astype(np.uint8),
                     "h": np.divide(h, (256 / bins)).astype(np.uint8),
                     "s": np.divide(s, (256 / bins)).astype(np.uint8),
                     "v": np.divide(v, (256 / bins)).astype(np.uint8)
                     }

    # Histogram plot types
    hist_types = {"ALL": ("b", "g", "r", "l", "m", "y", "h", "s", "v"),
                  "RGB": ("b", "g", "r"),
                  "LAB": ("l", "m", "y"),
                  "HSV": ("h", "s", "v")}

    if hist_plot_type is not None and hist_plot_type.upper() not in hist_types:
        fatal_error("The histogram plot type was " + str(hist_plot_type) +
                    ', but can only be one of the following: None, "all", "rgb", "lab", or "hsv"!')
    histograms = {
        "b": {"label": "blue", "graph_color": "blue",
              "hist": cv2.calcHist([norm_channels["b"]], [0], mask, [bins], [0, (bins - 1)])},
        "g": {"label": "green", "graph_color": "forestgreen",
              "hist": cv2.calcHist([norm_channels["g"]], [0], mask, [bins], [0, (bins - 1)])},
        "r": {"label": "red", "graph_color": "red",
              "hist": cv2.calcHist([norm_channels["r"]], [0], mask, [bins], [0, (bins - 1)])},
        "l": {"label": "lightness", "graph_color": "dimgray",
              "hist": cv2.calcHist([norm_channels["l"]], [0], mask, [bins], [0, (bins - 1)])},
        "m": {"label": "green-magenta", "graph_color": "magenta",
              "hist": cv2.calcHist([norm_channels["m"]], [0], mask, [bins], [0, (bins - 1)])},
        "y": {"label": "blue-yellow", "graph_color": "yellow",
              "hist": cv2.calcHist([norm_channels["y"]], [0], mask, [bins], [0, (bins - 1)])},
        "h": {"label": "hue", "graph_color": "blueviolet",
              "hist": cv2.calcHist([norm_channels["h"]], [0], mask, [bins], [0, (bins - 1)])},
        "s": {"label": "saturation", "graph_color": "cyan",
              "hist": cv2.calcHist([norm_channels["s"]], [0], mask, [bins], [0, (bins - 1)])},
        "v": {"label": "value", "graph_color": "orange",
              "hist": cv2.calcHist([norm_channels["v"]], [0], mask, [bins], [0, (bins - 1)])}
    }

    hist_data_b = [l[0] for l in histograms["b"]["hist"]]
    hist_data_g = [l[0] for l in histograms["g"]["hist"]]
    hist_data_r = [l[0] for l in histograms["r"]["hist"]]
    hist_data_l = [l[0] for l in histograms["l"]["hist"]]
    hist_data_m = [l[0] for l in histograms["m"]["hist"]]
    hist_data_y = [l[0] for l in histograms["y"]["hist"]]
    hist_data_h = [l[0] for l in histograms["h"]["hist"]]
    hist_data_s = [l[0] for l in histograms["s"]["hist"]]
    hist_data_v = [l[0] for l in histograms["v"]["hist"]]

    binval = np.arange(0, bins)
    bin_values = [l for l in binval]

    analysis_images = []
    dataset = pd.DataFrame({'bins': binval, 'blue': hist_data_b,
                            'green': hist_data_g, 'red': hist_data_r,
                            'lightness': hist_data_l, 'green-magenta': hist_data_m,
                            'blue-yellow': hist_data_y, 'hue': hist_data_h,
                            'saturation': hist_data_s, 'value': hist_data_v})

    # Make the histogram figure using plotnine
    if hist_plot_type is not None:
        if hist_plot_type.upper() == 'RGB':
            df_rgb = pd.melt(dataset, id_vars=['bins'], value_vars=['blue', 'green', 'red'],
                             var_name='Color Channel', value_name='Pixels')
            hist_fig = (ggplot(df_rgb, aes(x='bins', y='Pixels', color='Color Channel'))
                        + geom_line()
                        + scale_x_continuous(breaks=list(range(0, bins, 25)))
                        + scale_color_manual(['blue', 'green', 'red'])
                        )
            analysis_images.append(hist_fig)

        elif hist_plot_type.upper() == 'LAB':
            df_lab = pd.melt(dataset, id_vars=['bins'],
                             value_vars=['lightness', 'green-magenta', 'blue-yellow'],
                             var_name='Color Channel', value_name='Pixels')
            hist_fig = (ggplot(df_lab, aes(x='bins', y='Pixels', color='Color Channel'))
                        + geom_line()
                        + scale_x_continuous(breaks=list(range(0, bins, 25)))
                        + scale_color_manual(['yellow', 'magenta', 'dimgray'])
                        )
            analysis_images.append(hist_fig)

        elif hist_plot_type.upper() == 'HSV':
            df_hsv = pd.melt(dataset, id_vars=['bins'],
                             value_vars=['hue', 'saturation', 'value'],
                             var_name='Color Channel', value_name='Pixels')
            hist_fig = (ggplot(df_hsv, aes(x='bins', y='Pixels', color='Color Channel'))
                        + geom_line()
                        + scale_x_continuous(breaks=list(range(0, bins, 25)))
                        + scale_color_manual(['blueviolet', 'cyan', 'orange'])
                        )
            analysis_images.append(hist_fig)

        elif hist_plot_type.upper() == 'ALL':
            s = pd.Series(['blue', 'green', 'red', 'lightness', 'green-magenta',
                           'blue-yellow', 'hue', 'saturation', 'value'], dtype="category")
            color_channels = ['blue', 'yellow', 'green', 'magenta', 'blueviolet',
                              'dimgray', 'red', 'cyan', 'orange']
            df_all = pd.melt(dataset, id_vars=['bins'], value_vars=s, var_name='Color Channel',
                             value_name='Pixels')
            hist_fig = (ggplot(df_all, aes(x='bins', y='Pixels', color='Color Channel'))
                        + geom_line()
                        + scale_x_continuous(breaks=list(range(0, bins, 25)))
                        + scale_color_manual(color_channels)
                        )
            analysis_images.append(hist_fig)
            
    #flatten so that it is hashable
    h = h.flatten(order = 'C')
    
    # produces a dictionary with hue as key, and frequency as values.
    c = Counter(h)
    # remove background colour 
    del c[0]

    # sort the dictionary in order 
    ordered = dict(sorted(c.items(), key=lambda t: t[0]))

    # loop adds the hue to a list for the frequency of each hue
    temp_hue_list_hsv = []
    for i in range(len(ordered)):

        j = 0

        while j < list(ordered.values())[i]:
            temp_hue_list_hsv.append(list(ordered.keys())[i])

            j += 1

    #calculate relevant statistics 
    circular_mean = stats.circmean(temp_hue_list_hsv, 180)
    circular_std = stats.circstd(temp_hue_list_hsv, 180) # assumes samples are in the range [low to high] which they are

    median = np.median(temp_hue_list_hsv)

    # Store Color Histogram Data
    color_header = [
        'HEADER_COLOR',
        'bin-number',
        'bin-values',
        'blue',
        'green',
        'red',
        'lightness',
        'green-magenta',
        'blue-yellow',
        'hue',
        'saturation',
        'value',
        'circular_mean',
        'circular_std',
        'median'
    ]

    color_data = [
        'COLOR_DATA',
        bins,
        bin_values,
        hist_data_b,
        hist_data_g,
        hist_data_r,
        hist_data_l,
        hist_data_m,
        hist_data_y,
        hist_data_h,
        hist_data_s,
        hist_data_v,
        circular_mean,
        circular_std,
        median
    ]

    # Store into lists instead for pipeline and print_results
    # stats_dict = {'mean': circular_mean, 'std' : circular_std, 'median': median}

    # Plot or print the histogram
    if hist_plot_type is not None:
        if params.debug == 'print':
            hist_fig.save(os.path.join(params.debug_outdir, str(params.device) + '_analyze_color_hist.png'))
        elif params.debug == 'plot':
            print(hist_fig)

    # Store into global measurements
    if not 'color_data' in outputs.measurements:
        outputs.measurements['color_data'] = {}
    outputs.measurements['color_data']['bin-number'] = bins
    outputs.measurements['color_data']['bin-values'] = bin_values
    outputs.measurements['color_data']['blue'] = hist_data_b
    outputs.measurements['color_data']['green'] = hist_data_g
    outputs.measurements['color_data']['red'] = hist_data_r
    outputs.measurements['color_data']['lightness'] = hist_data_l
    outputs.measurements['color_data']['green-magenta'] = hist_data_m
    outputs.measurements['color_data']['blue-yellow'] = hist_data_y
    outputs.measurements['color_data']['hue'] = hist_data_h
    outputs.measurements['color_data']['saturation'] = hist_data_s
    outputs.measurements['color_data']['value'] = hist_data_v
    outputs.measurements['color_data']['mean'] = circular_mean
    outputs.measurements['color_data']['standard-deviation'] = circular_std
    outputs.measurements['color_data']['median'] = median

    # Store images
    outputs.images.append(analysis_images)

    return color_header, color_data, analysis_images
