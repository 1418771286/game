import pygame
import plane_main_1, plane_main_2, plane_main_3

#记得改标题
#屏幕的大小
SCREEN_RECT = pygame.Rect(0, 0, 573, 753)

class Menu(object):
    """每个页面的父类"""

    def __init__(self, image, music):

        #设置背景音乐
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

        #设置屏幕大小
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        #设置标题
        pygame.display.set_caption("英雄战机")
        #加载传入的图片并获取位置大小
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

    def event(self):
        #遍历所有事件
        for event in pygame.event.get():
            #点击游戏右上角的×关闭游戏
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            #按下Esc键关闭游戏
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        #获取鼠标是否点击和位置
        self.mouse_press = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

    @staticmethod
    def clicks():
        #点击按钮时播放声音
        pygame.mixer.music.load("./music/mouse.mp3")
        #设置声音大小
        pygame.mixer.music.set_volume(0.5)
        #0为不循环播放，start为从音频的什么时候开始。
        pygame.mixer.music.play(loops=0, start=0.5)
        #500毫秒的时间慢慢退出
        pygame.mixer.music.fadeout(500)


class MainMenu(Menu):
    """游戏主菜单"""

    def __init__(self):
        #加载背景音乐和图片
        music = "./music/menu1.mp3"
        image = "./images/background2.png"
        super().__init__(image, music)

    def update_menu(self):

        while True:

            #调用父类的事件方法
            super().event()

            #加载按钮并获取位置
            start = pygame.image.load("./images/start1.png")
            start_rect = start.get_rect()
            rule = pygame.image.load("./images/rule1.png")
            rule_rect = rule.get_rect()

            # 开始键和查看键位置定位
            start_rect.centerx = SCREEN_RECT.centerx
            start_rect.y = SCREEN_RECT.height * 0.3
            rule_rect.centerx = SCREEN_RECT.centerx
            rule_rect.y = SCREEN_RECT.height * 0.45

            #判断鼠标的横纵坐标是否在按钮图片范围内
            if (start_rect.left < self.mouse_pos[0] < start_rect.right) and (
                            start_rect.top < self.mouse_pos[1] < start_rect.bottom):
                #在图片范围内则更换图片
                start = pygame.image.load("./images/start2.png")
                #按下鼠标左键，触发父类的私有方法发出鼠标声，并跳转页面
                if self.mouse_press[0]:
                    Menu.clicks()
                    GameType().update_menu()

            if (rule_rect.left < self.mouse_pos[0] < rule_rect.right) and (
                            rule_rect.top < self.mouse_pos[1] < rule_rect.bottom):
                rule = pygame.image.load("./images/rule2.png")
                if self.mouse_press[0]:
                    Menu.clicks()
                    RuleMenu().update_menu()

            #更新背景、开始按钮、规则按钮
            self.screen.blit(self.image, self.rect)
            self.screen.blit(start, start_rect)
            self.screen.blit(rule, rule_rect)
            pygame.display.update()


class GameType(Menu):
    """游戏模式选择"""

    def __init__(self):
        music = "./music/type1.mp3"
        image = "./images/background4.png"
        super().__init__(image, music)

    def update_menu(self):

        while True:

            super().event()

            type1 = pygame.image.load("./images/first1.png")
            type1_rect = type1.get_rect()
            type2 = pygame.image.load("./images/second1.png")
            type2_rect = type2.get_rect()
            type3 = pygame.image.load("./images/third1.png")
            type3_rect = type3.get_rect()
            return_picture = pygame.image.load("./images/return5.png")
            return_rect = return_picture.get_rect()

            type1_rect.centerx = SCREEN_RECT.centerx
            type1_rect.y = SCREEN_RECT.height * 0.15
            type2_rect.centerx = type1_rect.centerx
            type2_rect.y = SCREEN_RECT.height * 0.3
            type3_rect.centerx = SCREEN_RECT.centerx
            type3_rect.y = SCREEN_RECT.height * 0.45
            return_rect.x = 10
            return_rect.y = 10

            #调用自己的静态私有方法获取记录
            record1 = self.__record(str(1))
            record2 = self.__record(str(2))

            # 开始模式一
            if (type1_rect.left < self.mouse_pos[0] < type1_rect.right) and (
                            type1_rect.top < self.mouse_pos[1] < type1_rect.bottom):
                type1 = pygame.image.load("./images/first2.png")
                if self.mouse_press[0]:
                    Menu.clicks()
                    plane_main_1.Game().start_game()

            #开始模式二
            if (type2_rect.left < self.mouse_pos[0] < type2_rect.right) and (
                            type2_rect.top < self.mouse_pos[1] < type2_rect.bottom):
                type2 = pygame.image.load("./images/second2.png")
                if self.mouse_press[0]:
                    Menu.clicks()
                    #用获取的记录判断能否开启游戏关卡
                    if 0 <= int(record1) <= 3:
                        plane_main_2.Game().start_game()
                    else:
                        #不可以则调用禁止类的，显示禁止页面
                        ProhibitMenu().update_menu()

            #开始模式三
            if (type3_rect.left < self.mouse_pos[0] < type3_rect.right) and (
                            type3_rect.top < self.mouse_pos[1] < type3_rect.bottom):
                type3 = pygame.image.load("./images/third2.png")
                if self.mouse_press[0]:
                    Menu.clicks()
                    if 0 <= int(record2) <= 3:
                        plane_main_3.Game().start_game()
                    else:
                        ProhibitMenu().update_menu()

            if return_rect.left < self.mouse_pos[0] < return_rect.right and (
                            return_rect.top < self.mouse_pos[1] < return_rect.bottom):
                return_picture = pygame.image.load("./images/return6.png")
                if self.mouse_press[0]:
                    Menu.clicks()
                    MainMenu().update_menu()

            self.screen.blit(self.image, self.rect)
            self.screen.blit(type1, type1_rect)
            self.screen.blit(type2, type2_rect)
            self.screen.blit(type3, type3_rect)
            self.screen.blit(return_picture, return_rect)
            pygame.display.update()

    @staticmethod
    def __record(num):
        #获取记录
        file = open("./text/c"+ num +".txt", "r")
        text = file.read()
        file.close()
        #返回记录
        if len(text) == 0:
            return 4
        else:
            return chr(int(text))


class RuleMenu(Menu):
    """游戏规则页面"""

    def __init__(self):

        music = "./music/rule1.mp3"
        image = "./images/background3.png"
        super().__init__(image, music)

    def update_menu(self):

        while True:
            super().event()

            return_picture = pygame.image.load("./images/return5.png")
            return_rect = return_picture.get_rect()

            return_rect.x = 10
            return_rect.y = 10

            if return_rect.left < self.mouse_pos[0] < return_rect.right and (
                            return_rect.top < self.mouse_pos[1] < return_rect.bottom):
                return_picture = pygame.image.load("./images/return6.png")

                if self.mouse_press[0]:
                    Menu.clicks()
                    MainMenu().update_menu()

            self.screen.blit(self.image, self.rect)
            self.screen.blit(return_picture, return_rect)
            pygame.display.update()


class ProhibitMenu(Menu):
    """禁止进入类"""

    def __init__(self):

        music = "./music/prohibit.mp3"
        image = "./images/prohibit.png"
        super().__init__(image, music)

    def update_menu(self):

        while True:

            super().event()

            return_picture = pygame.image.load("./images/return5.png")
            return_rect = return_picture.get_rect()

            return_rect.x= 10
            return_rect.y = 10

            if return_rect.left < self.mouse_pos[0] < return_rect.right and (
                            return_rect.top < self.mouse_pos[1] < return_rect.bottom):
                return_picture = pygame.image.load("./images/return6.png")
                if self.mouse_press[0]:
                    Menu.clicks()
                    GameType().update_menu()

            self.screen.blit(self.image, self.rect)
            self.screen.blit(return_picture, return_rect)
            pygame.display.update()

#开始
if __name__ == '__main__':
    #初始化pygame
    pygame.init()
    #初始化背景音乐播放器
    pygame.mixer.init()
    MainMenu().update_menu()