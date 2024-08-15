# -*- coding: utf-8 -*-
  

EDA for project
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.mixture import GaussianMixture as gmm
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

#keep the data file in the same folder as this file
df=pd.read_csv("smoke_detection_iot.csv")
df

"""Understanding the data"""

df.head()

df.tail()

df.shape

df.describe()

df.columns

df.nunique()

"""Cleaning the data"""

df.isnull().sum()

X=df.drop(["Fire Alarm","Unnamed: 0","UTC"],axis=1)
Y=df["Fire Alarm"]

X

Y

"""Relationship Analysis"""

correlation=X.corr()
correlation

redundant=pd.DataFrame()
Xupdated=X.copy()
for i in Xupdated.columns:
    for j in Xupdated.columns:
        c=X[i].corr(X[j])
        if(c>0.7 and c<1):
            redundant[i]=X[i]
            if(i in Xupdated.columns):
                Xupdated=Xupdated.drop([i],axis=1)
redundant

Xupdated

correlation1=Xupdated.corr()
correlation1

sns.heatmap(correlation1,xticklabels=correlation1.columns,yticklabels=correlation1.columns,annot=True)

newdf=pd.concat([Xupdated,Y], axis=1, join='inner')
newdf

#sns.pairplot(Xupdated)

# plots of pressure against other quantities were making some sense of clustering ,thus further exploring them

# sns.relplot(x="Pressure[hPa]",y="Temperature[C]",hue="Fire Alarm",data=newdf)
# sns.relplot(x="Pressure[hPa]",y="Humidity[%]",hue="Fire Alarm",data=newdf)
# sns.relplot(x="Pressure[hPa]",y="TVOC[ppb]",hue="Fire Alarm",data=newdf)
# sns.relplot(x="Pressure[hPa]",y="Raw H2",hue="Fire Alarm",data=newdf)
# sns.relplot(x="Pressure[hPa]",y="Raw Ethanol",hue="Fire Alarm",data=newdf)

"""Applying Normalisation"""

ss=StandardScaler()
standard_data=ss.fit_transform(Xupdated)

mm=MinMaxScaler()
normalised_data=mm.fit_transform(Xupdated)

standard_data

normalised_data

"""Applying PCA"""

#on normal data
pca=PCA(n_components=2)
Xpca=pca.fit_transform(Xupdated)

#on normalised data
normalised_data_pca=pca.fit_transform(normalised_data)

#on standardised data
standard_data_pca=pca.fit_transform(standard_data)

#splitting train and test data
smoke_detection=pd.concat([Xupdated,Y],axis=1, join='inner')

standard_data=pd.DataFrame(standard_data,columns=Xupdated.columns)
smoke_detection_standardised=pd.concat([standard_data,Y],axis=1, join='inner')
smoke_detection_standardised

normalised_data=pd.DataFrame(normalised_data,columns=Xupdated.columns)
smoke_detection_normalised=pd.concat([normalised_data,Y],axis=1, join='inner')
smoke_detection_normalised

smoke_detection_0=smoke_detection[smoke_detection['Fire Alarm']==0]
smoke_detection_1=smoke_detection[smoke_detection['Fire Alarm']==1]
smoke_detection_0

[x_train_0, x_test_0, x_label_train_0, x_label_test_0] = train_test_split(smoke_detection_0, smoke_detection_0['Fire Alarm'], test_size=0.3, random_state=42, shuffle=True)
x_train_1_per=len(x_train_0)/len(smoke_detection_1)
x_train_0=x_train_0.drop(['Fire Alarm'],axis=1)
[x_train_1, x_test_1, x_label_train_1, x_label_test_1] = train_test_split(smoke_detection_1, smoke_detection_1['Fire Alarm'], test_size=1-x_train_1_per, random_state=42, shuffle=True)
x_train_1_per
x_train_1=x_train_1.drop(['Fire Alarm'],axis=1)

x_train=pd.concat([x_train_0,x_train_1],axis=0)
x_train

x_test=pd.concat([x_test_0,x_test_1],axis=0)
x_test
x_test=x_test.drop(['Fire Alarm'],axis=1)

x_train_label=pd.concat([x_label_train_0,x_label_train_1],axis=0)
x_train_label=np.array(x_train_label)
x_train_label

x_test_label=pd.concat([x_label_test_0,x_label_test_1],axis=0)
x_test_label=np.array(x_test_label)
x_test_label

pure_data=[]
#using GMM
dic={}
def GMM(n):
    gmm_0=gmm(n_components=n,covariance_type='full',reg_covar=1e-5)
    #estimating parameters for gmm using train data
    gmm_0.fit(x_train_0)
    #making gaussian mixture model components for class 1
    gmm_1=gmm(n_components=n,covariance_type='full',reg_covar=1e-5)
        #estimating parameters for gmm using train data
    gmm_1.fit(x_train_1)
        #calculating list of loglikelihood for each test data tuple for both gmm_0 and gmm_1
    ll_0=gmm_0.score_samples(x_test)
    ll_1=gmm_1.score_samples(x_test)
        #making empty list to store predicted class using gmm classifier
    pred=[]
        #doing this so that i and j maps to same index element of ll_0 and ll_1 and calculating posterier for each data tuple separately
    for i,j in zip(ll_0,ll_1):
        #calculating likelihood for each test data tuple for both gmm_0 and gmm_1 or also called prior probability
        p_x_0=np.exp(i)
        p_x_1=np.exp(j)
        #calculating P(Ci)
        p_0=len(x_train_0)/(len(x_train_0)+len(x_train_1))
        p_1=len(x_train_1)/(len(x_train_0)+len(x_train_1))
        #Calculating posterior probability of each class
        p_0_x=p_x_0*p_0/(p_x_0*p_0+p_x_1*p_1)
        p_1_x=p_x_1*p_1/(p_x_0*p_0+p_x_1*p_1)
        if p_0_x>p_1_x:
            pred.append(0)
        else:
            pred.append(1)
    print('----- The confusion matrix using Bayes Classifier with GMM with Q =',n,' is -----')
    print()
    #giving output of confusion matix
    print(confusion_matrix(x_test_label,pred))
    print()
    print(accuracy_score(x_test_label, pred))
    #calculating accuracy
    acc=accuracy_score(x_test_label, pred)
    dic[n]=acc*100
for i in [2,4,8,16]:
    GMM(i)

#giving output for accuracy in form of dataframe
print(pd.DataFrame(zip(dic.keys(),dic.values()),columns=['Q','Accuracy(%)']))
acc_max=max(dic.values())
pure_data.append(acc_max)

#Decision Tree classifier

dtc=DecisionTreeClassifier()
dtc=dtc.fit(X=x_train,y=x_train_label)
pure_data.append((dtc.score(x_test,x_test_label))*100)

pred=dtc.predict(x_test)
print(confusion_matrix(x_test_label,pred))

#Random Forest Classifier
rfc=RandomForestClassifier()
rfc=rfc.fit(X=x_train,y=x_train_label)
pure_data.append((rfc.score(x_test,x_test_label))*100)
pred=dtc.predict(x_test)
print(confusion_matrix(x_test_label,pred))

#Bayes' Classifier
cov_0=np.array(x_train_0.cov())
#finding covariance matrix of train data of label 1
cov_1=np.array(x_train_1.cov())
#finding cmean array of train data of label 0
mean_0=np.array(x_train_0.mean())
#finding cmean array of train data of label 1
mean_1=np.array(x_train_1.mean())
#reshaping my mean array
np.reshape(mean_0,(1,len(x_train.columns)))
np.reshape(mean_1,(1,len(x_train.columns)))
pred=[]
def pred_class(x):
    #calculating likelihood for class 0 based on the formula for multivariate gaussian
    p_x_0=np.linalg.det((1/(((2*np.pi)**11.5)*(np.linalg.det(cov_0))**(0.5)))*np.exp(-0.5*np.matmul(np.matmul((x-mean_0),np.linalg.inv(cov_0)),(x-mean_0).T)))
    #calculating prior probability for class 0
    p_0=len(x_train_0)/len(x_train)
    #calculating likelihood for class 1 based on formula for multivariate gaussian
    p_x_1=np.linalg.det((1/(((2*np.pi)**11.5)*(np.linalg.det(cov_1))**(0.5)))*np.exp(-0.5*np.matmul(np.matmul((x-mean_1),np.linalg.inv(cov_1)),(x-mean_1).T)))
    #calculating prior probability for class 1
    p_1=len(x_train_1)/len(x_train)
    #calculating posterior probability for each class using baye's rule or baye's classifier
    p_0_x=p_x_0*p_0/(p_x_0*p_0+p_x_1*p_1)
    p_1_x=p_x_1*p_1/(p_x_0*p_0+p_x_1*p_1)
    #comparing probability to predict its class
    if p_0_x>p_1_x:
        return 0
    else:
        return 1
#creating a array to store predicted value for each class
pred=[]
#running a loop to get predicted class for each test_data
for i in x_test.index:
    pred.append(pred_class(np.array(x_test.loc[[i]])))

print(confusion_matrix(x_test_label,pred))
acc_3=accuracy_score(x_test_label, pred)
pure_data.append(acc_3*100)

smoke_detection_0=smoke_detection_normalised[smoke_detection_normalised['Fire Alarm']==0]
smoke_detection_1=smoke_detection_normalised[smoke_detection_normalised['Fire Alarm']==1]
smoke_detection_0

[x_train_0, x_test_0, x_label_train_0, x_label_test_0] = train_test_split(smoke_detection_0, smoke_detection_0['Fire Alarm'], test_size=0.3, random_state=42, shuffle=True)
x_train_1_per=len(x_train_0)/len(smoke_detection_1)
x_train_0=x_train_0.drop(['Fire Alarm'],axis=1)
[x_train_1, x_test_1, x_label_train_1, x_label_test_1] = train_test_split(smoke_detection_1, smoke_detection_1['Fire Alarm'], test_size=1-x_train_1_per, random_state=42, shuffle=True)
x_train_1_per
x_train_1=x_train_1.drop(['Fire Alarm'],axis=1)

x_train=pd.concat([x_train_0,x_train_1],axis=0)
x_train

x_test=pd.concat([x_test_0,x_test_1],axis=0)
x_test
x_test=x_test.drop(['Fire Alarm'],axis=1)

x_train_label=pd.concat([x_label_train_0,x_label_train_1],axis=0)
x_train_label=np.array(x_train_label)
x_train_label

x_test_label=pd.concat([x_label_test_0,x_label_test_1],axis=0)
x_test_label=np.array(x_test_label)
x_test_label

normalised_data=[]
#using GMM
dic={}
def GMM(n):
    gmm_0=gmm(n_components=n,covariance_type='full',reg_covar=1e-5)
    #estimating parameters for gmm using train data
    gmm_0.fit(x_train_0)
    #making gaussian mixture model components for class 1
    gmm_1=gmm(n_components=n,covariance_type='full',reg_covar=1e-5)
        #estimating parameters for gmm using train data
    gmm_1.fit(x_train_1)
        #calculating list of loglikelihood for each test data tuple for both gmm_0 and gmm_1
    ll_0=gmm_0.score_samples(x_test)
    ll_1=gmm_1.score_samples(x_test)
        #making empty list to store predicted class using gmm classifier
    pred=[]
        #doing this so that i and j maps to same index element of ll_0 and ll_1 and calculating posterier for each data tuple separately
    for i,j in zip(ll_0,ll_1):
        #calculating likelihood for each test data tuple for both gmm_0 and gmm_1 or also called prior probability
        p_x_0=np.exp(i)
        p_x_1=np.exp(j)
        #calculating P(Ci)
        p_0=len(x_train_0)/(len(x_train_0)+len(x_train_1))
        p_1=len(x_train_1)/(len(x_train_0)+len(x_train_1))
        #Calculating posterior probability of each class
        p_0_x=p_x_0*p_0/(p_x_0*p_0+p_x_1*p_1)
        p_1_x=p_x_1*p_1/(p_x_0*p_0+p_x_1*p_1)
        if p_0_x>p_1_x:
            pred.append(0)
        else:
            pred.append(1)
    print('----- The confusion matrix using Bayes Classifier with GMM with Q =',n,' is -----')
    print()
    #giving output of confusion matix
    print(confusion_matrix(x_test_label,pred))
    print()
    print(accuracy_score(x_test_label, pred))
    #calculating accuracy
    acc=accuracy_score(x_test_label, pred)
    dic[n]=acc*100
for i in [2,4,8,16]:
    GMM(i)

#giving output for accuracy in form of dataframe
print(pd.DataFrame(zip(dic.keys(),dic.values()),columns=['Q','Accuracy(%)']))
acc_max=max(dic.values())
normalised_data.append(acc_max)

#Decision Tree classifier

dtc=DecisionTreeClassifier()
dtc=dtc.fit(X=x_train,y=x_train_label)
normalised_data.append((dtc.score(x_test,x_test_label))*100)

#Random Forest Classifier
rfc=RandomForestClassifier()
rfc=rfc.fit(X=x_train,y=x_train_label)
normalised_data.append((rfc.score(x_test,x_test_label))*100)

#Bayes' Classifier
cov_0=np.array(x_train_0.cov())
#finding covariance matrix of train data of label 1
cov_1=np.array(x_train_1.cov())
#finding cmean array of train data of label 0
mean_0=np.array(x_train_0.mean())
#finding cmean array of train data of label 1
mean_1=np.array(x_train_1.mean())
#reshaping my mean array
np.reshape(mean_0,(1,len(x_train.columns)))
np.reshape(mean_1,(1,len(x_train.columns)))
pred=[]
def pred_class(x):
    #calculating likelihood for class 0 based on the formula for multivariate gaussian
    p_x_0=np.linalg.det((1/(((2*np.pi)**11.5)*(np.linalg.det(cov_0))**(0.5)))*np.exp(-0.5*np.matmul(np.matmul((x-mean_0),np.linalg.inv(cov_0)),(x-mean_0).T)))
    #calculating prior probability for class 0
    p_0=len(x_train_0)/len(x_train)
    #calculating likelihood for class 1 based on formula for multivariate gaussian
    p_x_1=np.linalg.det((1/(((2*np.pi)**11.5)*(np.linalg.det(cov_1))**(0.5)))*np.exp(-0.5*np.matmul(np.matmul((x-mean_1),np.linalg.inv(cov_1)),(x-mean_1).T)))
    #calculating prior probability for class 1
    p_1=len(x_train_1)/len(x_train)
    #calculating posterior probability for each class using baye's rule or baye's classifier
    p_0_x=p_x_0*p_0/(p_x_0*p_0+p_x_1*p_1)
    p_1_x=p_x_1*p_1/(p_x_0*p_0+p_x_1*p_1)
    #comparing probability to predict its class
    if p_0_x>p_1_x:
        return 0
    else:
        return 1
#creating a array to store predicted value for each class
pred=[]
#running a loop to get predicted class for each test_data
for i in x_test.index:
    pred.append(pred_class(np.array(x_test.loc[[i]])))

print(confusion_matrix(x_test_label,pred))
acc_3=accuracy_score(x_test_label, pred)
normalised_data.append(acc_3*100)

pure_data

normalised_data

moke_detection_0=smoke_detection_standardised[smoke_detection_standardised['Fire Alarm']==0]
smoke_detection_1=smoke_detection_standardised[smoke_detection_standardised['Fire Alarm']==1]
smoke_detection_0

[x_train_0, x_test_0, x_label_train_0, x_label_test_0] = train_test_split(smoke_detection_0, smoke_detection_0['Fire Alarm'], test_size=0.3, random_state=42, shuffle=True)
x_train_1_per=len(x_train_0)/len(smoke_detection_1)
x_train_0=x_train_0.drop(['Fire Alarm'],axis=1)
[x_train_1, x_test_1, x_label_train_1, x_label_test_1] = train_test_split(smoke_detection_1, smoke_detection_1['Fire Alarm'], test_size=1-x_train_1_per, random_state=42, shuffle=True)
x_train_1_per
x_train_1=x_train_1.drop(['Fire Alarm'],axis=1)

x_train=pd.concat([x_train_0,x_train_1],axis=0)
x_train

x_test=pd.concat([x_test_0,x_test_1],axis=0)
x_test
x_test=x_test.drop(['Fire Alarm'],axis=1)

x_train_label=pd.concat([x_label_train_0,x_label_train_1],axis=0)
x_train_label=np.array(x_train_label)
x_train_label

x_test_label=pd.concat([x_label_test_0,x_label_test_1],axis=0)
x_test_label=np.array(x_test_label)
x_test_label

standardised_data=[]
#using GMM
dic={}
def GMM(n):
    gmm_0=gmm(n_components=n,covariance_type='full',reg_covar=1e-5)
    #estimating parameters for gmm using train data
    gmm_0.fit(x_train_0)
    #making gaussian mixture model components for class 1
    gmm_1=gmm(n_components=n,covariance_type='full',reg_covar=1e-5)
        #estimating parameters for gmm using train data
    gmm_1.fit(x_train_1)
        #calculating list of loglikelihood for each test data tuple for both gmm_0 and gmm_1
    ll_0=gmm_0.score_samples(x_test)
    ll_1=gmm_1.score_samples(x_test)
        #making empty list to store predicted class using gmm classifier
    pred=[]
        #doing this so that i and j maps to same index element of ll_0 and ll_1 and calculating posterier for each data tuple separately
    for i,j in zip(ll_0,ll_1):
        #calculating likelihood for each test data tuple for both gmm_0 and gmm_1 or also called prior probability
        p_x_0=np.exp(i)
        p_x_1=np.exp(j)
        #calculating P(Ci)
        p_0=len(x_train_0)/(len(x_train_0)+len(x_train_1))
        p_1=len(x_train_1)/(len(x_train_0)+len(x_train_1))
        #Calculating posterior probability of each class
        p_0_x=p_x_0*p_0/(p_x_0*p_0+p_x_1*p_1)
        p_1_x=p_x_1*p_1/(p_x_0*p_0+p_x_1*p_1)
        if p_0_x>p_1_x:
            pred.append(0)
        else:
            pred.append(1)
    print('----- The confusion matrix using Bayes Classifier with GMM with Q =',n,' is -----')
    print()
    #giving output of confusion matix
    print(confusion_matrix(x_test_label,pred))
    print()
    print(accuracy_score(x_test_label, pred))
    #calculating accuracy
    acc=accuracy_score(x_test_label, pred)
    dic[n]=acc*100
for i in [2,4,8,16]:
    GMM(i)

#giving output for accuracy in form of dataframe
print(pd.DataFrame(zip(dic.keys(),dic.values()),columns=['Q','Accuracy(%)']))
acc_max=max(dic.values())
standardised_data.append(acc_max)

#Decision Tree classifier

dtc=DecisionTreeClassifier()
dtc=dtc.fit(X=x_train,y=x_train_label)
standardised_data.append((dtc.score(x_test,x_test_label))*100)

#Random Forest Classifier
rfc=RandomForestClassifier()
rfc=rfc.fit(X=x_train,y=x_train_label)
standardised_data.append((rfc.score(x_test,x_test_label))*100)

#Bayes' Classifier
cov_0=np.array(x_train_0.cov())
#finding covariance matrix of train data of label 1
cov_1=np.array(x_train_1.cov())
#finding cmean array of train data of label 0
mean_0=np.array(x_train_0.mean())
#finding cmean array of train data of label 1
mean_1=np.array(x_train_1.mean())
#reshaping my mean array
np.reshape(mean_0,(1,len(x_train.columns)))
np.reshape(mean_1,(1,len(x_train.columns)))
pred=[]
def pred_class(x):
    #calculating likelihood for class 0 based on the formula for multivariate gaussian
    p_x_0=np.linalg.det((1/(((2*np.pi)**11.5)*(np.linalg.det(cov_0))**(0.5)))*np.exp(-0.5*np.matmul(np.matmul((x-mean_0),np.linalg.inv(cov_0)),(x-mean_0).T)))
    #calculating prior probability for class 0
    p_0=len(x_train_0)/len(x_train)
    #calculating likelihood for class 1 based on formula for multivariate gaussian
    p_x_1=np.linalg.det((1/(((2*np.pi)**11.5)*(np.linalg.det(cov_1))**(0.5)))*np.exp(-0.5*np.matmul(np.matmul((x-mean_1),np.linalg.inv(cov_1)),(x-mean_1).T)))
    #calculating prior probability for class 1
    p_1=len(x_train_1)/len(x_train)
    #calculating posterior probability for each class using baye's rule or baye's classifier
    p_0_x=p_x_0*p_0/(p_x_0*p_0+p_x_1*p_1)
    p_1_x=p_x_1*p_1/(p_x_0*p_0+p_x_1*p_1)
    #comparing probability to predict its class
    if p_0_x>p_1_x:
        return 0
    else:
        return 1
#creating a array to store predicted value for each class
pred=[]
#running a loop to get predicted class for each test_data
for i in x_test.index:
    pred.append(pred_class(np.array(x_test.loc[[i]])))

print(confusion_matrix(x_test_label,pred))
acc_3=accuracy_score(x_test_label, pred)
standardised_data.append(acc_3*100)

standardised_data

a=['GMM','Decision_Tree','Random_forest','Bayes_classifier']
plt.bar(a,pure_data)
plt.title("Original_data")
plt.xlabel("classifier---->")
plt.ylabel("Accuracy---->")

a=['GMM','Decision_Tree','Random_forest','Bayes_classifier']
plt.bar(a,standardised_data)
plt.title("Standardised_data")
plt.xlabel("classifier---->")
plt.ylabel("Accuracy---->")

a=['GMM','Decision_Tree','Random_forest','Bayes_classifier']
plt.bar(a,normalised_data)
plt.title("Normalised_data")
plt.xlabel("classifier---->")
plt.ylabel("Accuracy---->")
