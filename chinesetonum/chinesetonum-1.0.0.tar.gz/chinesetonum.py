text = '两千八百二十三'
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
chineses = ['零', '一','二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '亿']
index = text.index('百')
temp = text[index-1:index]
position = chineses.index(temp)
print(position + 1)

