def chagechinesetonum(text):
    count = ['十', '百', '千', '万', '亿']
    numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    chineses = ['零', '一','二', '三', '四', '五', '六', '七', '八', '九']
    for item in text:
        if item in count:
            text = text.replace(item,'')
        else:
            if item == '两':
                text = text.replace(item,'2')
            else:
                index = chineses.index(item)
                text = text.replace(item,str(numbers[index]))
    return int(text)

