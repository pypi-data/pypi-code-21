import numpy as np

class Model():
    def __init__(self, gender, article_type, xg_model):
        self.model = xg_model
        
        self.word2vec = [('Men','Tshirts'),('Men','Shirts'), ('Men', 'Jeans'), \
        ('Men','Trousers'), ('Women','Jeans'),('Women','Kurtas')]
        
        self.gender = gender
        self.article_type = article_type

        self.user_vector_lengths = {
            ('Men','Jackets') : 39,
            ('Men','Sweatshirts') : 39,
            ('Men','Sweaters') : 39,
            ('Men','Blazers') : 39,
            ('Men','Kurtas') : 39,
            ('Men','Shorts') : 37,
            ('Women','Shorts') : 37,
            ('Women','Sweaters') : 39,            
            ('Women','Sweatshirts') : 39,
            ('Women','Jackets') : 39,
            ('Women','Tunics') : 43,
            ('Women','Kurtis') : 43,
            ('Women','Tshirts') : 39,
            ('Women','Shirts') : 39,
            ('Women', 'Dresses') : 43,
            ('Women', 'Tops') : 43 
        }

    def get_prediction(self,user_vector, style_dict):
        gender = self.gender
        article_type = self.article_type

        predicted_sku = None

        if article_type in ['Jeans', 'Trousers','Shorts']:
            main_diff = 2
        else:
            main_diff = 2
        
        #u_main_dim = self.get_main_dimension(user_vector)

        u_main_dim = user_vector[100]

        v_list = []
        diff_list = []
        predicted_sku_list = []
        for p_sku_id in style_dict:
            
            if (gender, article_type) in self.word2vec:
                main_dim = style_dict[p_sku_id][100]
            else:
                main_dim = style_dict[p_sku_id][100]
                    
            if abs(main_dim - u_main_dim) <= main_diff:
                test_vector = list(user_vector) + list(style_dict[p_sku_id]) 
                v_list.append(test_vector)
                predicted_sku_list.append(p_sku_id)
                diff_list.append(abs(main_dim - u_main_dim))

        if len(v_list) <= 0:
            return None

        if min(diff_list) > 2:
            return None

        v_list = np.array(v_list)

        pro = self.model.predict_proba(v_list)
        predicted_pro = [x[1] for x in pro]
        i = np.argmax(predicted_pro)
        predicted_sku = predicted_sku_list[i]

        return predicted_sku

    def get_main_dimension(self,user_vector):
        gender = self.gender
        article_type = self.article_type

        if (gender, article_type) in self.word2vec:
            return user_vector[100]
        else:
            u1 = user_vector[32]
            l = self.user_vector_lengths[(gender, article_type)]
            u2 = user_vector[l + 100]
            if u1 < 1.0:
                return u2
            return u1 