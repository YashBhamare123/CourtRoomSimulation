import pandas as pd
#
# # Read the CSV files, explicitly dropping any 'Unnamed: 0' column if it exists
# df = pd.read_csv('spam.csv', index_col=False)
# df_real = pd.read_csv('/Users/yash/Downloads/cases_final.csv', index_col=False)
#
# # Drop 'Unnamed: 0' column if it exists in either DataFrame
# if 'Unnamed: 0' in df.columns:
#     df = df.drop(columns=['Unnamed: 0'])
# if 'Unnamed: 0' in df_real.columns:
#     df_real = df_real.drop(columns=['Unnamed: 0'])
#
# # Create the df2 DataFrame with ID and VERDICT
# out_list = [0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1]
# df2 = pd.DataFrame({'ID': df_real['id'][0:33], 'VERDICT': out_list})
#
# # Merge df and df2 on the 'ID' column
# df = pd.concat([df, df2], axis = 0, ignore_index= True)
#
# # Save the result to 'output.csv' without including the index
# df.to_csv('output.csv', index=False)

df = pd.read_csv('spam.csv', index_col= False)
df.drop(df.columns[df.columns.str.contains('Unnamed', case=False)], axis=1, inplace=True)
df.to_csv('next_out.csv', index = False)
