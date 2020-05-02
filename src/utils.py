import os
import re
from datetime import datetime
import pandas as pd
import numpy as np
from constants import RESULTS_DIRECTORY, COLUMNS_TO_KEEP, COLUMNS_NAMES


def get_formated_telephone(telephone):
    if not telephone:
        return ""

    telephone = re.sub('[^0-9/]', '', telephone)

    if telephone.startswith('0'):
        telephone = telephone[1:]

    if telephone.startswith("549"):
        telephone = telephone[3:]

    telephones = telephone.split("/")

    return telephones[0]


def merge_result_files(path):
    directory = os.path.join(path,
                             RESULTS_DIRECTORY,
                             datetime.today().strftime('%Y-%m-%d'))
    dfs = []
    for filename in os.listdir(directory):
        if not filename.endswith('.csv'):
            continue
        site = filename.split('_')[0]
        df = pd.read_csv(os.path.join(directory, filename))
        if site == 'zonaprop':
            df = df[COLUMNS_TO_KEEP[site]]
            df['Tel'] = np.nan
            df['Tel2'] = np.nan
        elif site == 'lavoz':
            df = df[COLUMNS_TO_KEEP[site]]
        elif site == 'meli':
            df['publication_date'] = np.nan
            df = df[COLUMNS_TO_KEEP[site]]
        else:
            continue

        df.columns = COLUMNS_NAMES
        df['Sitio'] = site
        dfs.append(df)

    merged_df = pd.concat(dfs)
    merged_df.to_csv(os.path.join(directory, 'base_unida.csv'), index=False)
