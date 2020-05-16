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

            avg_daily_measure = round(statistics.mean(hourly_measures), 2)

            data.append({
                'date': datestamp,
                'station': monitor_station,
                'type': CODE_MAP[code],
                'daily_avg': avg_daily_measure
            })

        return data


def airquality_2020_trend():
    df = pd.DataFrame([])
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_01_Gener_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_02_Febrer_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_03_Marc_qualitat_aire_BCN.csv")))
    df = df.append(pd.DataFrame(
        parse_bcn_airquality_data_file("2020_04_Abril_qualitat_aire_BCN.csv")))

    df = df.groupby(['date', 'type'], as_index=False)['daily_avg'].mean()

    df = pd.pivot_table(df, index='date', columns='type',
                        values='daily_avg', fill_value=0)

    # Calculate average value over 7 days
    df = df.rolling(7).mean().dropna()

    # Build and render chart

    chart = pygal.StackedLine(
        title=u'Barcelona Air Quality - 2020 Overview',
        x_title="Average over 7 days",
        x_label_rotation=20,
        fill=True,
        show_dots=False,
        show_minor_x_labels=False
    )

    dates = df.index.tolist()

    chart.x_labels = dates
    chart.add('NO', df['NO'])
    chart.add('NO2', df['NO2'])
    chart.add('NOx', df['NOx'])
    chart.add('PM10', df['PM10'])
    chart.add('SO2', df['SO2'])
    chart.x_labels_major = dates[::7]

    chart.render_to_file(OUTPUT_DIR + 'airquality_overview_2020_Jan-Apr.svg')


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
    style = pygal.style.DefaultStyle()

    # NO2
    chart = pygal.HorizontalBar(
        title=u'Barcelona Air Quality - NO2 Apr 2019 vs 2020',
        x_title="micrograms per cubic meter air µg/m³",
        x_label_rotation=20,
        show_dots=False,
        style=style
    )

    chart.x_labels = dates
    chart.add('Apr 2019 - NO2', df_apr_2019['NO2'])
    chart.add('Apr 2020 - NO2', df_apr_2020['NO2'])

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
    chart.add('Apr 2019 - PM10', df_apr_2019['PM10'])
    chart.add('Apr 2020 - PM10', df_apr_2020['PM10'])

    chart.render_to_file(OUTPUT_DIR + 'airquality_apr19-20-PM10.svg')


if __name__ == "__main__":
    airquality_2020_trend()
    airquality_april_to_april()
