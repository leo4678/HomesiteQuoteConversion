import random
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.cross_validation import train_test_split,cross_val_score
from sklearn import preprocessing

# Reading files 

train = pd.read_csv("pywp/train.csv")
test = pd.read_csv('pywp/test.csv')

#train_sample = np.random.choice(train.index.values,40000)   
#train = train.ix[train_sample]
#train.to_csv("pywp/train_sample.csv",index=False)

y = train.QuoteConversion_Flag.values

train['Date'] = pd.to_datetime(pd.Series(train['Original_Quote_Date']))
train = train.drop('Original_Quote_Date', axis=1)   

test['Date'] = pd.to_datetime(pd.Series(test['Original_Quote_Date']))
test = test.drop('Original_Quote_Date', axis=1)

## Seperating date into 3 columns
train['Year'] = train['Date'].apply(lambda x: int(str(x)[:4]))
train['Month'] = train['Date'].apply(lambda x: int(str(x)[5:7]))
train['weekday'] = train['Date'].dt.dayofweek

test['Year'] = test['Date'].apply(lambda x: int(str(x)[:4]))
test['Month'] = test['Date'].apply(lambda x: int(str(x)[5:7]))
test['weekday'] = test['Date'].dt.dayofweek 
    
train = train.drop('Date', axis=1)
test = test.drop('Date', axis=1)    

## Filing NA values with -1

train.fillna(-1,inplace=True)
test.fillna(-1,inplace=True)

## Converting categorical variables into numeric variables with label encoder

for f in train.columns:
    if train[f].dtype=='object':
        lbl=preprocessing.LabelEncoder()
        lbl.fit(list(train[f].values)+list(test[f].values))
        train[f]=lbl.transform(list(train[f].values))
        test[f]=lbl.transform(list(test[f].values))

train = train.drop(['QuoteNumber','QuoteConversion_Flag','PropertyField6', 'GeographicField10A'], axis=1)
test = test.drop(['QuoteNumber','PropertyField6', 'GeographicField10A'],axis=1)

golden_feature=[("CoverageField1B","PropertyField21B"),
                ("GeographicField6A","GeographicField8A"),
                ("GeographicField6A","GeographicField13A"),
                ("GeographicField8A","GeographicField13A"),
                ("GeographicField11A","GeographicField13A"),
                ("GeographicField8A","GeographicField11A")]

for featureA,featureB in golden_feature:
      train["_".join([featureA,featureB,"diff"])]=train[featureA]-train[featureB]
      test["_".join([featureA,featureB,"diff"])]=test[featureA]-test[featureB]

#train = train.drop(['QuoteNumber', 'QuoteConversion_Flag'], axis=1)
#test = test.drop('QuoteNumber', axis=1)    

#X = train.ix[:, 0:299]
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)    t   
      
extc = ExtraTreesClassifier(n_estimators=1000,random_state =50,max_features= 303,criterion= 'entropy',min_samples_split= 3,
                            max_depth= 25, min_samples_leaf= 12)      
extc.fit(train,y)          
        
## Creating submission file

preds = extc.predict_proba(test)[:,1]
sample = pd.read_csv('pywp/sample_submission.csv')
sample.QuoteConversion_Flag = preds
sample.to_csv('pywp/extcter1000goldenfea.csv', index=False)        
      
