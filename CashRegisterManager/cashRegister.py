import time

userData = {
    "hw": "201700800067",
    "wjm": "201700800094",
}

# 检查登录
def checkLogIn(logInCount) :
    print("欢迎进入收银管理系统，请登录")
    while logInCount > 0 :
        userName = input("用户名: ")
        password = input("密码: ")
        logInCount -= 1
        # 检查用户名和密码是否匹配
        if userData.get(userName) == None or userData.get(userName) != password:
            if logInCount > 0:
                print("登录失败,请重新登录,您还有{0}次机会:".format(logInCount))
            else :
                print("对不起，登录失败,您已无法继续登录")
                return False
        else :
            print("登录成功")
            return True
    
    return False

# 检查输入的商品信息
def inputItems():
    print("欢迎您,请您输入商品信息")
    itemList = []
    # 输入商品信息
    while True:
        item = [0.0, 0]
        itemPrice = input("请输入商品单价:")
        itemAmount = input("请输入商品数量:")
        # 检查是否为正确格式
        if type(eval(itemAmount)) != int or not (type(eval(itemPrice)) == int or type(eval(itemPrice)) == float):
            print("对不起,您输入的数据的格式不正确,请重新输入")
            continue
        # 取价格和数量，价格保留一位小数
        itemPrice = round(eval(itemPrice) , 1)
        itemAmount = eval(itemAmount)
        item[0] = itemPrice
        item[1] = itemAmount
        
        # 检查边界条件，防止非正数输入
        if itemPrice <= 0 or itemAmount <= 0.0:
            print("对不起,您输入的数据的格式不正确,请重新输入")
            continue
            
        itemList.append(item)

        # 提示结束输入
        if input("您是否要结束输入商品信息?按[Y]退出").lower() == 'y':
            break
    # 获取总价格和总数量
    totalAmount = 0
    totalPrice = 0.0
    for item in itemList:
        totalAmount += item[1]
        totalPrice += item[0] * item[1]
    print("您本次选购商品:{}件, 总价为:{}元".format(totalAmount, totalPrice))
    print("感谢惠顾,欢迎下次光临")
    return itemList, totalAmount, totalPrice 

# 打印商品清单
def printItemList(itemList, totalAmount, totalPrice):
    # 以时间名做文件名生成订单
    orderFile = time.strftime("./transactions/%Y-%m-%d-%H-%M-%S.txt", time.localtime())
    fileWriter = open(orderFile, 'w', encoding="utf-8")
    fileWriter.seek(0, 0)
    # 将订单写入文件
    for i in range(len(itemList)):
        itemMessage = "商品{0}: 单价 {1}元, 数量 {2}个\n".format(i+1, itemList[i][0], itemList[i][1])
        fileWriter.write(itemMessage)
    totalMessage = "总量: {}个\n总价: {}元\n".format(totalAmount, totalPrice)
    fileWriter.write(totalMessage)
    fileWriter.close()

# 主函数
def main():
    if checkLogIn(4) == False:
        exit()
    itemList, totalAmount, totalPrice = inputItems()
    # 检查是否有合法商品
    if totalAmount > 0:
        printItemList(itemList, totalAmount, totalPrice)
    
main()