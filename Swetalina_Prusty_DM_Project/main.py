# Required Libraries
import pandas as pd

def comparision_check(df, num_days):
    per180 = df[df['Sensor Glucose (mg/dL)'] > 180].groupby(['Date']).count()
    per180 = (per180['Time'].sum() * 100) / (288 * num_days)
    per250 = df[df['Sensor Glucose (mg/dL)'] > 250].groupby(['Date']).count()
    per250 = (per250['Time'].sum() * 100) / (288 * num_days)
    per70_180 = df[df['Sensor Glucose (mg/dL)'].between(70, 180)].groupby(['Date']).count()
    per70_180 = (per70_180['Time'].sum() * 100) / (288 * num_days)
    per70_150 = df[df['Sensor Glucose (mg/dL)'].between(70, 150)].groupby(['Date']).count()
    per70_150 = (per70_150['Time'].sum() * 100) / (288 * num_days)
    per70 = df[df['Sensor Glucose (mg/dL)'] < 70].groupby(['Date']).count()
    per70 = (per70['Time'].sum() * 100) / (288 * num_days)
    per54 = df[df['Sensor Glucose (mg/dL)'] < 54].groupby(['Date']).count()
    per54 = (per54['Time'].sum() * 100) / (288 * num_days)
    return per180, per250, per70_180, per70_150, per70, per54


def remove_outliers(df, date_df, date):
    modechange_date = date.strftime('%m-%d-%Y')
    modechange_date = '/'.join([x[1] if x[0] == '0' else x for x in modechange_date.split('/')])
    indexes = list(date_df[(date_df['Time'] > 288) | (date_df['Time'] < 263)].index) + [modechange_date]
    df = df.drop(df[df['Date'].isin(indexes)].index, axis=0)
    return df


def get_all_dfs(cgm_df, mode_change_index):
    manual_df = cgm_df[:mode_change_index]
    auto_df = cgm_df[mode_change_index:]
    whole_manual_df = manual_df.set_index('DateTime')
    day_manual_df = whole_manual_df.between_time('06:00:00', '23:59:59')
    night_manual_df = whole_manual_df.between_time('00:00:00', '05:59:59')
    whole_auto_df = auto_df.set_index('DateTime')
    day_auto_df = whole_auto_df.between_time('06:00:00', '23:59:59')
    night_auto_df = whole_auto_df.between_time('00:00:00', '05:59:59')
    return whole_manual_df, day_manual_df, night_manual_df, whole_auto_df, day_auto_df, night_auto_df


# Importing data from InsulinData CSV file
insulin_df = pd.read_csv("InsulinData.csv")

# Reversing the rows to get increase order of time
insulin_df = insulin_df[::-1]

# Combining Date and Time columns
insulin_df['DateTime'] = insulin_df['Date'] + " " + insulin_df['Time']

# Converting DateTime column to datetime format
insulin_df['DateTime'] = pd.to_datetime(insulin_df['DateTime'])

# Storing the DateTime values when the sensor mode changes from manual to auto
mode_change_time_stamps = insulin_df[insulin_df['Alarm'] == 'AUTO MODE ACTIVE PLGM OFF']['DateTime']
mode_change_date = mode_change_time_stamps.iloc[0]

# Importing data from CGMData CSV file
cgm_df = pd.read_csv("CGMData.csv")

# Reversing the rows to get increase order of time
cgm_df = cgm_df[::-1]

# Combining Date and Time columns
cgm_df['DateTime'] = cgm_df['Date'] + " " + cgm_df['Time']

# Converting DateTime column to datetime format
cgm_df['DateTime'] = pd.to_datetime(cgm_df['DateTime'])

# Taking specific columns
cgm_df = cgm_df[['Date', 'Time', 'DateTime', 'Sensor Glucose (mg/dL)']]

# Grouping the glucose data by each day
cgm_day_count = cgm_df.groupby(['Date']).count()

# Removing the days with day count less than 263 and greater than 288
cgm_df = remove_outliers(cgm_df, cgm_day_count, mode_change_date)

# Filling missing values
cgm_df['Sensor Glucose (mg/dL)'] = cgm_df['Sensor Glucose (mg/dL)'].interpolate(method='linear', limit_direction='both')

# Finding the index at which the mode is getting changed
mode_change_index = len(cgm_df[cgm_df['DateTime'] <= mode_change_date])

# Creating multiple Dataframes
whole_manual_df, day_manual_df, night_manual_df, whole_auto_df, day_auto_df, night_auto_df = get_all_dfs(cgm_df,
                                                                                                       mode_change_index)

# Finding the number of days when the sensor in manual mode
manual_days_count = whole_manual_df.groupby(['Date']).count()
num_manual_days = manual_days_count.count()[0]

# Manual-Mode

# Whole day Metrics
whole_manual_per180, whole_manual_per250, whole_manual_per70_180, whole_manual_per70_150, whole_manual_per70, whole_manual_per54 = comparision_check(
    whole_manual_df, num_manual_days)

# Daytime Metrics
day_manual_per180, day_manual_per250, day_manual_per70_180, day_manual_per70_150, day_manual_per70, day_manual_per54 = comparision_check(
    day_manual_df, num_manual_days)
# Nighttime Metrics

night_manual_per180, night_manual_per250, night_manual_per70_180, night_manual_per70_150, night_manual_per70, night_manual_per54 = comparision_check(
    night_manual_df, num_manual_days)

# Auto-Mode

# Finding the number of days the sensor is in auto mode
auto_days_count = whole_auto_df.groupby(['Date']).count()
num_auto_days = auto_days_count.count()[0]

# Whole day Metrics
whole_auto_per180, whole_auto_per250, whole_auto_per70_180, whole_auto_per70_150, whole_auto_per70, whole_auto_per54 = comparision_check(
    whole_auto_df, num_auto_days)

# Daytime Metrics
day_auto_per180, day_auto_per250, day_auto_per70_180, day_auto_per70_150, day_auto_per70, day_auto_per54 = comparision_check(
    day_auto_df, num_auto_days)

# Nighttime Metrics
night_auto_per180, night_auto_per250, night_auto_per70_180, night_auto_per70_150, night_auto_per70, night_auto_per54 = comparision_check(
    night_auto_df, num_auto_days)

# Output to CSV
output_df = pd.DataFrame([[night_manual_per180, night_manual_per250, night_manual_per70_180, night_manual_per70_150,
                          night_manual_per70, night_manual_per54, day_manual_per180, day_manual_per250,
                          day_manual_per70_180, day_manual_per70_150, day_manual_per70, day_manual_per54,
                          whole_manual_per180, whole_manual_per250, whole_manual_per70_180, whole_manual_per70_150,
                          whole_manual_per70, whole_manual_per54],
                         [night_auto_per180, night_auto_per250, night_auto_per70_180, night_auto_per70_150,
                          night_auto_per70, night_auto_per54, day_auto_per180, day_auto_per250, day_auto_per70_180,
                          day_auto_per70_150, day_auto_per70, day_auto_per54, whole_auto_per180, whole_auto_per250,
                          whole_auto_per70_180, whole_auto_per70_150, whole_auto_per70, whole_auto_per54]],
                        columns=['Percentage time in hyperglycemia (CGM > 180 mg/dL)',
                                 'Percentage of time in hyperglycemia critical (CGM > 250 mg/dL)',
                                 'Percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL)',
                                 'Percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL)',
                                 'Percentage time in hypoglycemia level 1 (CGM < 70 mg/dL)',
                                 'Percentage time in hypoglycemia level 2 (CGM < 54 mg/dL)'] * 3,
                        index=['Manual Mode', 'Auto Mode'])
output_df = output_df.fillna(0)
output_df.to_csv('Results.csv', header = False, index = False)
