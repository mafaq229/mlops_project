import os
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression, Ridge,Lasso
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import RandomizedSearchCV
from catboost import CatBoostRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_model


@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join("artifacts", "model.pkl")


class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        
    def initiate_model_trainer(self, train_array, test_array):
        try:
            logging.info("Split training and test input data")
            X_train, y_train, X_test, y_test = train_array[:, :-1], train_array[:,-1], test_array[:, :-1], test_array[:,-1]
            models = {
                "Linear Regression": LinearRegression(),
                "K-Neighbors Regressor": KNeighborsRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Random Forest Regressor": RandomForestRegressor(),
                "XGBRegressor": XGBRegressor(), 
                "CatBoosting Regressor": CatBoostRegressor(verbose=False),
                "AdaBoost Regressor": AdaBoostRegressor(),
                "Decision Tree": DecisionTreeRegressor()
            }
            # these models retain their trained state (inside evaluate_model()) in the models dictionary.
            # When you iterate over the models dictionary and train each model using fit, you're directly updating the model instances stored in the dictionary.
            # when you assign an object to a variable or store it in a dictionary, you're working with a reference to the object, not a copy.
            model_report: dict = evaluate_model(X_train=X_train, y_train=y_train, 
                                                X_test=X_test, y_test=y_test, models=models)
            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]
            if best_model_score < 0.6:
                raise CustomException("No best model found")
            logging.info("Best found model on both training and testing dataset")
            
            save_object(file_path=self.model_trainer_config.trained_model_file_path, obj=best_model)
            predicted = best_model.predict(X_test)
            r2 = r2_score(y_test, predicted)
            return r2
            
        except Exception as e:
            raise CustomException(e, sys)
