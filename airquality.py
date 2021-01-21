import csv
import statistics
import pandas as pd
import json
import datetime
import pygal

DATA_FILE_DAILY = 'Qualitat_Aire_Detall.csv'
CODE_MAP = {
    1: 'SO2',
    7: 'NO',
    8: 'NO2',
    12: 'NOx',
    14: 'O3',
    6:  'CO',
    10: 'PM10'
}

OUTPUT_DIR = 'output/'

style = pygal.style.LightSolarizedStyle(
    colors=('#e86258', '#ffec12', '#14e35d', '#53f5ed', '#b753f5'))


def parse_bcn_airquality_data_file(filename):
    with open('data/' + filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = []
        for row in reader:
            monitor_station = int(row['ESTACIO'])
            code = int(row['CODI_CONTAMINANT'])

            # Skip codes not in the known map (unsure why there is such data...)
            if code not in CODE_MAP:
                break

            year = int(row['ANY'])
            month = f"{int(row['MES']):02d}"
            day = f"{int(row['DIA']):02d}"

            datestamp = datetime.datetime.strptime(
                f"{day}{month}{year}", '%d%m%Y').date()

            # Don't care about hourly measures so will change this into daily average
            hourly_measures = []
            for hour in range(1, 25):
                hour_key = f"{hour:02d}"
                validation_key = "V" + hour_key
                data_key = "H" + hour_key
                # Only record validated data
                if row[validation_key] == 'V':
                    hourly_measures.append(float(row[data_key]))

            # Only calculate and add average if we have data
            if hourly_measures:
                avg_daily_measure = round(statistics.mean(hourly_measures), 2)

                data.append({
                    'date': datestamp,
                    'station': monitor_station,
                    'type': CODE_MAP[code],
                    'daily_avg': avg_daily_measure
                })

        return data


def get_2020_trend_df(average_over=7):
    df = pd.DataFrame([])
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_01_Gener_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_02_Febrer_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_03_Marc_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_04_Abril_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_05_Maig_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_06_Juny_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_07_Juliol_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_08_Agost_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_09_Setembre_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_10_Octubre_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_11_Novembre_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_12_Desembre_qualitat_aire_BCN.csv")))

    df = df.groupby(['date', 'type'], as_index=False)['daily_avg'].mean()

    df = pd.pivot_table(df, index='date', columns='type',
                        values='daily_avg', fill_value=0)

    # Calculate average value over X days
    df = df.rolling(average_over).mean().dropna()

    return df


def airquality_2020_trend():
    df = get_2020_trend_df(14)
    # Build and render chart

    chart = pygal.Line(
        title=u'Barcelona Air Quality - 2020 Overview',
        y_title="micrograms per cubic meter air µg/m³",
        x_title="Average over 14 days",
        x_label_rotation=20,
        fill=False,
        show_dots=False,
        show_minor_x_labels=False,
        style=style
    )

    dates = df.index.tolist()

    chart.x_labels = dates
    chart.add('NO', df['NO'])
    chart.add('NO2', df['NO2'])
    chart.add('NOx', df['NOx'])
    chart.add('PM10', df['PM10'])
    chart.add('SO2', df['SO2'])
    chart.x_labels_major = dates[::14]

    chart.render_to_file(
        OUTPUT_DIR + 'airquality_overview_2020.svg')
    chart.render_to_png(
        OUTPUT_DIR + 'airquality_overview_2020.png')


def airquality_2020_trend_no2():
    df = get_2020_trend_df(14)

    # Build and render chart

    chart = pygal.Line(
        title=u'Barcelona Air Quality - 2020 NO2 Overview',
        y_title="micrograms per cubic meter air µg/m³",
        x_title="Average over 14 days",
        x_label_rotation=20,
        fill=True,
        show_dots=False,
        show_minor_x_labels=False,
        style=style,
        x_value_formatter=lambda dt: dt.strftime('%d, %b')
    )

    dates = df.index.tolist()

    chart.x_labels = dates
    chart.add('NO2', df['NO2'])
    chart.x_labels_major = dates[::14]

    chart.render_to_file(
        OUTPUT_DIR + 'airquality_overview_2020_No2.svg')
    chart.render_to_png(
        OUTPUT_DIR + 'airquality_overview_2020_No2.png')


def airquality_april_to_april():
    df_apr_2019 = pd.DataFrame(parse_bcn_airquality_data_file(
        "2019_04_Abril_qualitat_aire_BCN.csv"))

    df_apr_2019 = df_apr_2019.groupby(['date', 'type'], as_index=False)[
        'daily_avg'].mean()

    df_apr_2019 = pd.pivot_table(df_apr_2019, index='date', columns='type',
                                 values='daily_avg', fill_value=0)

    df_apr_2020 = pd.DataFrame(parse_bcn_airquality_data_file(
        "2020_04_Abril_qualitat_aire_BCN.csv"))

    df_apr_2020 = df_apr_2020.groupby(['date', 'type'], as_index=False)[
        'daily_avg'].mean()

    df_apr_2020 = pd.pivot_table(df_apr_2020, index='date', columns='type',
                                 values='daily_avg', fill_value=0)

    # Build and render charts
    dates = df_apr_2020.index.tolist()
    # style = pygal.style.LightSolarizedStyle()

    # NO2
    chart = pygal.HorizontalBar(
        title=u'Barcelona Air Quality - NO2 Apr 2019 vs 2020',
        x_title="micrograms per cubic meter air µg/m³",
        x_label_rotation=20,
        show_dots=False,
        style=style
    )

    chart.x_labels = dates
    chart.add('Apr 2019', df_apr_2019['NO2'])
    chart.add('Apr 2020', df_apr_2020['NO2'])

    chart.render_to_file(OUTPUT_DIR + 'airquality_apr19-20-NO2.svg')

    # PM10
    chart = pygal.HorizontalBar(
        title=u'Barcelona Air Quality - PM10 Apr 2019 vs 2020',
        x_title="micrograms per cubic meter air µg/m³",
        x_label_rotation=20,
        show_dots=False,
        style=style
    )

    chart.x_labels = dates
    chart.add('Apr 2019', df_apr_2019['PM10'])
    chart.add('Apr 2020', df_apr_2020['PM10'])

    chart.render_to_file(OUTPUT_DIR + 'airquality_apr19-20-PM10.svg')


if __name__ == "__main__":
    airquality_2020_trend()
    airquality_2020_trend_no2()
    airquality_april_to_april()
