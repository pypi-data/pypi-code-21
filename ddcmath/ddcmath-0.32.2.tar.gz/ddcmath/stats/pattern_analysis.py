class UnnaturalPatternMixin():
    def unnatural_pattern_detection(self, chart_type = None):
        if chart_type is 'r':
            df = self._df_R
        elif chart_type is 'x':
            df = self._df_X
        else:
            df = self._df
        for i, value in enumerate(df['values']):
            if value > df['sigma3'][0] or value < df['sigma-3'][0]:
                df.loc[df.index[i],'x'] = True
            
            if i >= 2:
                if df['values'][i-3:i][df['values'] > df['sigma2'][0]].count() >= 2 \
                or df['values'][i-3:i][df['values'] < df['sigma-2'][0]].count() >= 2:
                    if df['values'][i] > df['sigma2'][0] \
                    or df['values'][i] < df['sigma-2'][0]:
                        df.loc[df.index[i-1],'x'] = True
                    else:
                        df.loc[df.index[i-3],'x'] = True
                    
            if i >= 4:
                if df['values'][i-5:i][df['values'] > df['sigma1'][0]].count() >= 4 \
                or df['values'][i-5:i][df['values'] < df['sigma-1'][0]].count() >= 4:
                    if df['values'][i] > df['sigma1'][0] \
                    or df['values'][i] < df['sigma-1'][0]:
                        df.loc[df.index[i-1],'x'] = True
                    elif df['values'][i-1] > df['sigma1'][0] \
                    or df['values'][i-1] < df['sigma-1'][0]:
                        df.loc[df.index[i-2],'x'] = True
                    else:
                        df.loc[df.index[i-3],'x'] = True

            if i >= 7:
                if df['values'][i-8:i][df['values'] > df['mean'][0]].count() == 8 \
                or df['values'][i-8:i][df['values'] < df['mean'][0]].count() == 8:
                    #print('record %s : 8 consecutive above / below mean' % i)
                    df.loc[df.index[i],'x'] = True

            # Mixture
            if i >= 8:
                if df['values'][i-8:i][(df['values'] < df['sigma1'][0]) & (df['values'] > df['sigma-1'][0])].count() == 0 \
                and df['values'][i-8:i][df['values'] > df['sigma1'][0]].count() >= 3 \
                and df['values'][i-8:i][df['values'] < df['sigma-1'][0]].count() >= 3 :
                    df.loc[df.index[i],'mixture'] = True
                    
            # Stratification
            if i >= 15:
                if df['values'][i-15:i][(df['values'] < df['sigma1'][0]) & (df['values'] > df['sigma-1'][0])].count() == 15 :
                    df.loc[df.index[i],'stratification'] = True
            if chart_type is 'r':
                self._df_R = df
            elif chart_type is 'x':
                self._df_X = df
            else:
                self._df = df
