import astropy.io.fits as fits
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy import wcs
import os
from astropy.coordinates import SkyCoord


plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.color'] = 'red'
plt.rcParams['ytick.color'] = 'red'


def get_wcs(data_name):
    """
    得到wcs信息
    :param data_name: fits文件
    :return:
    data_wcs
    """
    data_header = fits.getheader(data_name)
    keys = data_header.keys()
    key = [k for k in keys if k.endswith('4')]
    [data_header.remove(k) for k in key]
    data_header.remove('VELREF')
    data_wcs = wcs.WCS(data_header)
    return data_wcs


def make_plot_11(data_mask_plot, spectrum_max, spectrum_mean, Cen3, Peak3, title_name, save_path):

    bottom_123 = 0.66
    pad = 0.005
    width = 0.01
    fig = plt.figure(figsize=(10, 8))
    ax1 = fig.add_axes([0.1, bottom_123, 0.28, 0.28])
    ax2 = fig.add_axes([0.4, bottom_123, 0.28, 0.28])
    ax3 = fig.add_axes([0.7, bottom_123, 0.28, 0.28])
    ax4 = fig.add_axes([0.1, 0.33, 0.8, 0.28])

    im0 = ax1.imshow(data_mask_plot.sum(0), origin='lower')  # x银纬,y银经
    im1 = ax2.imshow(data_mask_plot.sum(1), origin='lower')  # x银纬，y速度
    im2 = ax3.imshow(data_mask_plot.sum(2), origin='lower')  # x银经，y速度

    ax1.set_xlabel('latitude', fontsize=8)
    ax1.set_ylabel('Longitude', fontsize=8)
    ax2.set_xlabel('Latitude', fontsize=8)
    ax2.set_ylabel('Velocity', fontsize=8)
    ax2.set_title(title_name, fontsize=12)
    ax3.set_xlabel('Longitude', fontsize=8)
    ax3.set_ylabel('Velocity', fontsize=8)

    pos = ax1.get_position()
    axes1 = fig.add_axes([pos.xmax + pad, pos.ymin, width, 1 * (pos.ymax - pos.ymin)])
    cbar = fig.colorbar(im0, cax=axes1)
    # cbar.set_label('K m s${}^{-1}$')

    pos = ax2.get_position()
    axes2 = fig.add_axes([pos.xmax + pad, pos.ymin, width, 1 * (pos.ymax - pos.ymin)])
    cbar = fig.colorbar(im1, cax=axes2)

    pos = ax3.get_position()
    axes3 = fig.add_axes([pos.xmax + pad, pos.ymin, width, 1 * (pos.ymax - pos.ymin)])
    cbar = fig.colorbar(im2, cax=axes3)
    # plt.xticks([]), plt.yticks([])

    line3, = ax4.plot(spectrum_max)
    line4, = ax4.plot([Peak3, Peak3], [spectrum_max.min(), spectrum_max.max() * 1.2], 'b--')
    ax4.set_ylabel('K [T]')
    line3.set_label('Maximum spectrum')
    line4.set_label('Peak3')
    ax4.legend()

    ax5 = fig.add_axes([0.1, 0.05, 0.8, 0.28])
    line1,  = ax5.plot(spectrum_mean)
    line2,  = ax5.plot([Cen3, Cen3], [spectrum_mean.min(), spectrum_mean.max() * 1.2], 'b--')
    line1.set_label('Average spectrum')
    line2.set_label('Cen3')
    ax5.legend()
    ax5.set_xlabel('Velocity [pixels]')
    ax5.set_ylabel('K [T]')

    save_fig_path = os.path.join(save_path, '%s.png') % title_name
    fig.savefig(save_fig_path)
    plt.close()


def make_plot_wcs(data_name, loc_outcat_wcs_name, outcat_wcs_name):
    # data_name = r'R2_data\data_9\0180-005\0180-005_L.fits'
    fits_path = data_name.replace('.fits', '')
    title = fits_path.split('\\')[-1]
    # loc_outcat_wcs_name = os.path.join(fits_path, 'LDC_loc_outcat_wcs.txt')
    # outcat_wcs_name = os.path.join(fits_path, 'LDC_outcat_wcs.txt')
    fig_name = os.path.join(fits_path, title + '.png')

    outcat_wcs = pd.read_csv(outcat_wcs_name, sep='\t')
    loc_outcat_wcs = pd.read_csv(loc_outcat_wcs_name, sep='\t')

    wcs = get_wcs(data_name)
    data_cube = fits.getdata(data_name)

    loc_outcat_wcs_c = SkyCoord(frame="galactic", l=loc_outcat_wcs['Cen1'].values, b=loc_outcat_wcs['Cen2'].values,
                                unit="deg")
    outcat_wcs_c = SkyCoord(frame="galactic", l=outcat_wcs['Cen1'].values, b=outcat_wcs['Cen2'].values, unit="deg")

    fig = plt.figure(figsize=(5, 4.25), dpi=100)

    axes0 = fig.add_axes([0.15, 0.1, 0.7, 0.82], projection=wcs.celestial)
    axes0.set_xticks([])
    axes0.set_yticks([])
    im0 = axes0.imshow(data_cube.sum(axis=0))
    axes0.plot_coord(outcat_wcs_c, 'r*', markersize=2.5)
    axes0.plot([30, 30], [30, 90], 'r')
    axes0.plot([90, 30], [30, 30], 'r')
    axes0.plot([90, 90], [30, 90], 'r')
    axes0.plot([90, 30], [90, 90], 'r')

    axes0.set_xlabel("Galactic Longutide", fontsize=12)
    axes0.set_ylabel("Galactic Latitude", fontsize=12)
    axes0.set_title(title, fontsize=12)
    pos = axes0.get_position()
    pad = 0.01
    width = 0.02
    axes1 = fig.add_axes([pos.xmax + pad, pos.ymin, width, 1 * (pos.ymax - pos.ymin)])

    cbar = fig.colorbar(im0, cax=axes1)
    cbar.set_label('K m s${}^{-1}$')

    plt.savefig(fig_name)
    # shutil.copy(fig_name, os.path.join(r'R2_data\hh', title + '.png'))
    plt.close()


def deal_data(path_detect, path_save_fig, loc=False):
    """

    对检测的结果，将每个云核进行可视化
    处理数据并调用 make_plot_11()画图

    :param path_detect: 一个Cell检测结果保存的路径
    :param path_save_fig: 对云核可视化的保存路径
    :return:
    """

    """
    :param path_outcat: 像素核表
    :param path_outcat_wcs: 经纬度核表
    :param path_data: 数据
    :param path_mask: 掩膜
    :param path_save_fig: 图片保存路径
    :param v_len: 谱线速度轴的1/2（自己定义）
    :return:
    """
    if not os.path.exists(path_save_fig):
        os.mkdir(path_save_fig)

    v_len = 30
    if loc:
        path_outcat = os.path.join(path_detect, 'LDC_auto_loc_outcat.csv')
        path_outcat_wcs = os.path.join(path_detect, 'LDC_auto_loc_outcat_wcs.csv')
    else:
        path_outcat = os.path.join(path_detect, 'LDC_auto_outcat.csv')
        path_outcat_wcs = os.path.join(path_detect, 'LDC_auto_outcat_wcs.csv')

    path_mask = os.path.join(path_detect, 'LDC_auto_mask.fits')
    detect_log = os.path.join(path_detect, 'LDC_auto_detect_log.txt')
    f = open(detect_log)
    file_name = [item for item in f.readlines() if item.count('fits')]
    f.close()
    file_name = file_name[0].split(' ')[-1][:-1]
    path_data = file_name

    table_LDC = pd.read_csv(path_outcat, sep='\t')  # 像素核表
    table_LDC_wcs = pd.read_csv(path_outcat_wcs, sep='\t')  # 经纬度核表

    data = fits.getdata(path_data)  # 数据
    mask = fits.getdata(path_mask)  # 掩膜
    [size_v, size_y, size_x] = mask.shape

    expend = 1
    for item_i, item in enumerate(table_LDC['ID']):
        item = int(item)
        peak1 = table_LDC['Peak1'][item_i]
        peak2 = table_LDC['Peak2'][item_i]
        peak3 = table_LDC['Peak3'][item_i]
        cen3 = table_LDC['Cen3'][item_i]
        title_name = table_LDC_wcs['ID'][item_i]

        mask1 = mask.copy()
        mask1[mask1 != item] = 0
        clump_item = data * mask1 / item
        [a, b, c] = np.where(clump_item != 0)
        aa = np.array([[a.min() - expend, 0], [a.max() + 1 + expend, size_v]])
        bb = np.array([[b.min() - expend, 0], [b.max() + 1 + expend, size_y]])
        cc = np.array([[c.min() - expend, 0], [c.max() + 1 + expend, size_x]])
        clump_item_loc = clump_item[aa[0].max(): aa[1].min(), bb[0].max(): bb[1].min(), cc[0].max(): cc[1].min()]

        v_range = np.array([[int(peak3 - v_len), 0], [int(peak3 + v_len), size_v - 1]])
        data_i_max = np.zeros(v_len * 2)
        data_i_mean_ = np.zeros(v_len * 2)

        data_i_max[:v_range[1].min() - v_range[0].max()] = data[v_range[0].max(): v_range[1].min(), int(peak2) - 1, int(peak1) - 1]

        data_i_mean = clump_item[v_range[0].max(): v_range[1].min(), bb[0].max(): bb[1].min(), cc[0].max(): cc[1].min()]
        for i in range(v_range[1].min() - v_range[0].max()):
            data_i_mean_[i] = data_i_mean[i, ...].mean()

        loc_cen3 = cen3 - v_range[0].max()-1
        loc_peak3 = peak3 - v_range[0].max()-1

        make_plot_11(clump_item_loc, data_i_max, data_i_mean_, loc_cen3, loc_peak3, title_name, path_save_fig)


if __name__ == '__main__':
    path_detect = r'F:\DensityClust_distribution_class\0155+030_L'

    path_save_fig = path_detect
    deal_data(path_detect, path_save_fig,loc=True)
