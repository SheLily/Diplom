from vkinder import VKinder

if __name__ == '__main__':
    token = input('Введите токен пользователя')
    v = VKinder(token)
    result = v.do()
    print('Результат сохранен в файл с текущей датой и временем')
