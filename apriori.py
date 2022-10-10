import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from settings import dataset_path

# Loading the dataset
df = pd.read_excel(dataset_path, sheet_name='Data')
codebook = pd.read_excel(dataset_path, sheet_name='Codebook')
data=(df[df['Gender']!='Combined'])
data = data.drop(['Subregion'], axis=1)
data = data.groupby(['Region']).mean()
data.reset_index(inplace=True)
data = data.drop(['Region','Year'], axis=1)
data=data.dropna(how='any',axis=1)
#data.to_csv('Idea.ys.csv',index=False)

# delete variable name (codebook) if not exist in data
ind=[]
for i in range(len(codebook)):
    if codebook.iloc[i,0] not in data.columns:
        ind.append(codebook[(codebook["Variable"]==codebook.iloc[i,0])].index[0])
codebook.drop(index=ind,inplace=True)

cb1 = codebook[['[old] Parameter or Survey Question', 'Answer Label or Code','Variable']]

def occ(df,cb) :
    list=[]
    dff=df.copy()
    i=0
    while i < len(df.columns):
        var_name = df.columns[i]
        for row in cb.values:
            if (row[2] == var_name) :
                question=row[0]
                count=cb['[old] Parameter or Survey Question'].value_counts()[question]
                if count >1 : list.append(count)
                else :  dff.drop(df.columns[i], axis=1, inplace=True)
                i+=count
    return dff,list

dff,val=occ(data,cb1)

def prepare_data_for_apriori(df,list):
    dff=df.copy()
    i=0
    while i < len(df):
        j=0
        k=0
        while (j<len(df.columns) and k<len(list)) :
            for x in range(list[k]):
                # if(df.iloc[i,j:j+list[k]].max().max() == df.iloc[i,j+x]):
                if(df.iloc[i,j:j+list[k]].max() == df.iloc[i,j+x]):
                    dff.iloc[i,j+x]=1
                else:
                    dff.iloc[i,j+x]=0
            j+=list[k]
            k+=1
        i+=1
    return dff
w=prepare_data_for_apriori(dff,val)

df = apriori(w, min_support = 0.01, use_colnames = True, verbose = 1)
#Let's view our interpretation values using the Associan rule function.
ar = association_rules(df, metric = "confidence", min_threshold = 0.6)

ar["antecedents"] = ar["antecedents"].apply(lambda x: ', '.join(list(x))).astype("unicode")
ar["consequents"] = ar["consequents"].apply(lambda x: ', '.join(list(x))).astype("unicode")
data=ar[~ar.consequents.str.contains(',')]
ar=data[~data.antecedents.str.contains(",")]