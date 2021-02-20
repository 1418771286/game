import pygame
import main
from sprites_2 import *

#敌机出现事件
CREATE_ENEMY_EVENT = pygame.USEREVENT
#队友出现事件
CREATE_TEAMMATE_EVENT = pygame.USEREVENT + 1
#boss发射子弹
BOSS_FIRE_EVENT = pygame.USEREVENT + 2
#雪花出现
CREATE_SNOWFLAKE_EVENT = pygame.USEREVENT + 3
#火焰出现
CREATE_FLAME_EVENT = pygame.USEREVENT + 4


#发射子弹间隔
HERO_FIRE_SPACE = 25
#boss子弹发射时间间隔
BOSS_SHOOT = 4000
#创建敌机时间间隔
ENEMY_HAPPEN_TIME = 4000
#创建队友时间间隔
TEAMMATE_HAPPEN = 6000
#创建雪花时间
SNOWFLAKE_HAPPEN = 2500
#创建火焰时间
FLAME_HAPPEN = 3500
#游戏帧数
RATE = 100


class Game(object):
    """主程序"""

    #初始化
    def __init__(self, ):
        #背景音乐
        pygame.mixer.init()
        self.music = "./music/play2.mp3"
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        #屏幕大小和标题
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        pygame.display.set_caption("冰火试炼")

        #设置两种字体
        self.font1 = pygame.font.Font("./font/STXINWEI.TTF", 25)
        self.font2 = pygame.font.Font("./font/STXINWEI.TTF", 50)

        self.clock = pygame.time.Clock()    #设置游戏时钟
        self.hero_speed = 3                 #初始英雄移动速度
        self.score = 0                      #记录友军死亡数
        self.is_win = True                  #判断游戏是否能赢
        self.slowly = False                 #判断雪花击中飞机减速
        self.quickly = False                #判断火焰击中飞机加速

        self.__create_sprites()
        #调用函数返回历史记录
        self.history_score = Game.__record()
        Game.__create_event()

    #创建精灵组
    def __create_sprites(self):
        #背景精灵组
        self.back_group = pygame.sprite.Group(Background(), Background(True))

        #英雄精灵；英雄和队友精灵组
        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)
        self.teammate_group = pygame.sprite.Group()

        #boss精灵；boss和敌人精灵组
        self.boss = EnemyBoss()
        self.boss_group = pygame.sprite.Group(self.boss)
        self.enemy_group = pygame.sprite.Group()

        #雪花和火焰精灵组
        self.snowflake_group = pygame.sprite.Group()
        self.flame_group = pygame.sprite.Group()

        #爆炸精灵组
        self.destroy_group = pygame.sprite.Group()

    #创建事件
    @staticmethod
    def __create_event():

        #创建敌机时间间隔
        pygame.time.set_timer(CREATE_ENEMY_EVENT, ENEMY_HAPPEN_TIME)
        #创建队友时间间隔
        pygame.time.set_timer(CREATE_TEAMMATE_EVENT, TEAMMATE_HAPPEN)
        #boss子弹发射时间间隔
        pygame.time.set_timer(BOSS_FIRE_EVENT, BOSS_SHOOT)
        #雪花飘落的时间间隔
        pygame.time.set_timer(CREATE_SNOWFLAKE_EVENT, SNOWFLAKE_HAPPEN)
        #火焰掉落的时间间隔
        pygame.time.set_timer(CREATE_FLAME_EVENT, FLAME_HAPPEN)

    #英雄血量显示
    def hero_blood(self, life = 3):
        if life == 3:
            blood1 = pygame.image.load("./images/blood1.png")
        elif life == 2:
            blood1 = pygame.image.load("./images/blood2.png")
        elif life == 1:
            blood1 = pygame.image.load("./images/blood3.png")
        else:
            blood1 = pygame.image.load("./images/blood4.png")
        blood1_rect = blood1.get_rect()
        blood1_rect.right = SCREEN_RECT.right
        blood1_rect.bottom = SCREEN_RECT.height - 10
        self.screen.blit(blood1, blood1_rect)

    #boss血量显示
    def boss_blood(self, life):
        if life == 0:
            blood2 = pygame.image.load("./images/bbl1.png")
        elif life >= 30:
            blood2 = pygame.image.load("./images/bbl11.png")
        else:
            num = life // 3 + 2
            blood2 = pygame.image.load("./images/bbl" + str(num) + ".png")
        blood2_rect = blood2.get_rect()
        blood2_rect.centerx = SCREEN_RECT.centerx
        blood2_rect.bottom = SCREEN_RECT.top + 30
        self.screen.blit(blood2, blood2_rect)

    #开始游戏
    def start_game(self):

        while True:
            #设置帧数
            self.clock.tick(RATE)

            self.__event_handler()
            self.__update_sprites()
            self.__collide_check()

            #在屏幕上输出数据
            self.print_text(10, 0,
                            "历史最低伤亡：%s" % self.history_score)

            #输出英雄生命值
            self.hero_blood(self.hero.life)

            #计算boss总血量
            boss_all_life = self.boss.life + EnemyBoss.enemy_die
            if boss_all_life <= 0:
                boss_all_life = 0
            if self.boss.rect.top >= SCREEN_RECT.top + 0.5 * self.boss.rect.height:
                self.boss_blood(boss_all_life)
            self.print_text(SCREEN_RECT.width - 190, 0,
                            "BOSS生命值×{:.0f}".format(boss_all_life))
            self.print_text(SCREEN_RECT.width - 150, 30,
                            "友军阵亡：{:.0f}".format(self.score))

            #更新屏幕
            pygame.display.update()

    #事件监控
    def __event_handler(self):

        #获取所有按键
        keys_pressed = pygame.key.get_pressed()
        
        #判断是否要减速
        if self.slowly:
            self.hero_speed = 2
            self.slowly = False
        elif self.quickly and self.hero_speed == 2:
            self.hero_speed = 3
            self.quickly = False
        elif self.quickly and self.hero_speed == 3:
            self.hero_speed = 4
            self.hero.life -= 1
            self.quickly = False
            
        #英雄移动控制
        if keys_pressed[pygame.K_w]:
            self.hero.speed = [0, -self.hero_speed]
            if keys_pressed[pygame.K_a]:
                self.hero.speed = [-self.hero_speed, -self.hero_speed]
            elif keys_pressed[pygame.K_d]:
                self.hero.speed = [self.hero_speed, -self.hero_speed]
            elif keys_pressed[pygame.K_s]:
                self.hero.speed = [0, 0]
        elif keys_pressed[pygame.K_s]:
            self.hero.speed = [0, self.hero_speed]
            if keys_pressed[pygame.K_a]:
                self.hero.speed = [-self.hero_speed, self.hero_speed]
            elif keys_pressed[pygame.K_d]:
                self.hero.speed = [self.hero_speed, self.hero_speed]
        elif keys_pressed[pygame.K_a]:
            self.hero.speed = [-self.hero_speed, 0]
            if keys_pressed[pygame.K_d]:
                self.hero.speed = [0, 0]
        elif keys_pressed[pygame.K_d]:
            self.hero.speed = [self.hero_speed, 0]

        # 上下左右控制
        if keys_pressed[pygame.K_UP]:
            self.hero.speed = [0, -self.hero_speed]
            if keys_pressed[pygame.K_LEFT]:
                self.hero.speed = [-self.hero_speed, -self.hero_speed]
            elif keys_pressed[pygame.K_RIGHT]:
                self.hero.speed = [self.hero_speed, -self.hero_speed]
            elif keys_pressed[pygame.K_DOWN]:
                self.hero.speed = [0, 0]
        elif keys_pressed[pygame.K_DOWN]:
            self.hero.speed = [0, self.hero_speed]
            if keys_pressed[pygame.K_LEFT]:
                self.hero.speed = [-self.hero_speed, self.hero_speed]
            elif keys_pressed[pygame.K_RIGHT]:
                self.hero.speed = [self.hero_speed, self.hero_speed]
        elif keys_pressed[pygame.K_LEFT]:
            self.hero.speed = [-self.hero_speed, 0]
            if keys_pressed[pygame.K_RIGHT]:
                self.hero.speed = [0, 0]
        elif keys_pressed[pygame.K_RIGHT]:
            self.hero.speed = [self.hero_speed, 0]

        #子弹发射控制
        self.hero.fire_space += 1
        if self.hero.fire_space >= HERO_FIRE_SPACE:
            self.hero.fire_space = HERO_FIRE_SPACE
        if keys_pressed[pygame.K_j]:
            if self.hero.fire_space % HERO_FIRE_SPACE == 0:
                self.hero.fire()
                self.hero.fire_space = 0

        #遍历所有事件
        for event in pygame.event.get():

            # 结束游戏控制
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()

            # 键盘释放，停止英雄移动
            if event.type == pygame.KEYUP:
                self.hero.speed = [0, 0]

            #敌机出现频率控制
            if event.type == CREATE_ENEMY_EVENT:
                self.enemy1 = Enemy()
                self.enemy_group.add(self.enemy1)


            #队友出现频率控制
            if event.type == CREATE_TEAMMATE_EVENT:
                self.teammate1 = Teammate()
                self.teammate_group.add(self.teammate1)

            #雪花出现事件
            if event.type == CREATE_SNOWFLAKE_EVENT:
                self.snowflake = Snowflake()
                self.snowflake_group.add(self.snowflake)

            if event.type == CREATE_FLAME_EVENT:
                self.flame = Flame()
                self.flame_group.add(self.flame)

            #boss发射子弹
            if event.type == BOSS_FIRE_EVENT and self.boss.speed[1] == 0:
                self.boss.fire()
                #boss死后清除子弹
                # if len(self.boss_group) == 0:
                #     self.boss.bullet2_group.kill()

    #碰撞检测
    def __collide_check(self):

        #英雄与敌机碰撞事件，返回装有敌机的列表
        for enemy in pygame.sprite.spritecollide(
                self.hero, self.enemy_group,True):
            self.destroy_group.add(enemy)
            self.enemy_group.remove(enemy)
            #调用destroied（）方法播放摧毁图片
            enemy.destroied()
            self.hero.life -= 1
            if self.hero.life <= 0:
                self.hero.destroied()

        #英雄与队友碰撞
        for teammate in pygame.sprite.spritecollide(
                self.hero, self.teammate_group, True):
            self.destroy_group.add(teammate)
            self.teammate_group.remove(teammate)
            # 调用destroied（）方法播放摧毁图片
            teammate.destroied()
            self.score += 1
            self.hero.life -= 1
            if self.hero.life <= 0:
                self.hero.destroied()

        # 英雄与boss碰撞
        for enemy in pygame.sprite.spritecollide(
                self.hero, self.boss_group, True):
            self.destroy_group.add(enemy)
            self.enemy_group.remove(enemy)
            enemy.destroied()
            self.hero.destroied()

        #子弹1和敌机碰撞，返回装有敌机的字典
        enemies = pygame.sprite.groupcollide(
            self.enemy_group, self.hero.bullet1_group, False, True).keys()
        for enemy in enemies:
            enemy.life -= 1
            if enemy.life <= 0:
                self.destroy_group.add(enemy)
                self.enemy_group.remove(enemy)
                enemy.destroied()

        #子弹1和队友碰撞
        teammates = pygame.sprite.groupcollide(
            self.teammate_group, self.hero.bullet1_group, False, True).keys()
        for teammate in teammates:
            teammate.life -= 1
            if teammate.life <= 0:
                self.destroy_group.add(teammate)
                self.teammate_group.remove(teammate)
                teammate.destroied()
                self.score += 1

        # 子弹1打boss
        boss_all_life = self.boss.life + EnemyBoss.enemy_die
        enemy_boss = pygame.sprite.groupcollide(
            self.boss_group, self.hero.bullet1_group, False, True).keys()
        for enemy in enemy_boss:
            enemy.life -= 2
            if boss_all_life <= 1:  #测试时发现要-1血boss才会毁灭
                self.destroy_group.add(enemy)
                self.enemy_group.remove(enemy)
                enemy.destroied()

        # 子弹2射中英雄
        for _ in pygame.sprite.spritecollide(
                self.hero, self.boss.bullet2_group, True):
            self.hero.life -= 1
            if self.hero.life <= 0:
                self.hero.destroied()

        # 雪花打中英雄
        for _ in pygame.sprite.spritecollide(
                self.hero, self.snowflake_group, True):
            sound = pygame.mixer.Sound('./music/ice1.wav')
            sound.set_volume(0.6)
            sound.play()
            sound.fadeout(3000)
            self.slowly = True

        # 火焰打中英雄
        for _ in pygame.sprite.spritecollide(
                self.hero, self.flame_group, True):
            sound = pygame.mixer.Sound('./music/flame2.wav')
            sound.set_volume(0.4)
            sound.play()
            sound.fadeout(1500)
            self.quickly = True


        #英雄可以销毁就结束游戏
        if self.hero.can_destroied:
            #播放失败音效
            pygame.mixer.music.stop()
            sound = pygame.mixer.Sound('./music/fail1.wav')
            sound.set_volume(0.3)
            sound.play()

            self.is_win = False
            Game.over_page(self, False)

        #boss可以销毁结束游戏，同时防止同归于尽boss先死
        elif self.boss.can_destroied and self.is_win == True:
            #更新分数
            if self.score < 10:
                self.update_record()

            pygame.mixer.music.stop()
            sound = pygame.mixer.Sound('./music/win.wav')
            sound.set_volume(0.3)
            sound.play()

            Game.over_page(self)

    #字体输出函数
    def print_text(self, x, y, text, color = (255, 255, 255), font=1):
        self.text = text
        if font == 1:
            imgText1 = self.font1.render(self.text, True, color)
            self.screen.blit(imgText1, (x, y))
        if font == 2:
            imgText2 = self.font2.render(self.text, True, color)
            self.screen.blit(imgText2, (x, y))

    #历史记录
    @staticmethod
    def __record():
        file = open("./text/c2.txt", "r")
        text = file.read()
        file.close()
        if len(text) == 0:
            return "无"
        else:
            return chr(int(text))

    #更新记录
    def update_record(self):

        file = open("./text/c2.txt", "r")
        text = file.read()
        file.close()
        if len(text) == 0:
            encrypt = ord("{}".format(self.score))
            file = open("./text/c2.txt", "w")
            file.write(str(encrypt))
            file.close()

        else :
            decrypt = chr(int(text))
            if self.score < int(decrypt):
                decrypt = self.score
                encrypt = ord("{}".format(decrypt))
                file = open("./text/c2.txt", "w")
                file.write(str(encrypt))
                file.close()

    #更新精灵组
    def __update_sprites(self):

        for group in [self.back_group, self.hero_group,
                      self.enemy_group, self.destroy_group,
                      self.hero.bullet1_group, self.teammate_group,
                      self.boss_group, self.boss.bullet2_group,
                      self.snowflake_group, self.flame_group]:

            group.update()
            group.draw(self.screen)

    #鼠标点击图标声音实现
    @staticmethod
    def clicks():
        pygame.mixer.music.load("./music/mouse.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=0, start=0.5)
        pygame.mixer.music.fadeout(500)

    #结束时的页面
    def over_page(self, victory=True):
        """结束界面"""

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

            mouse_press = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            image = pygame.image.load("./images/background1.png")
            rect = image.get_rect()

            if self.is_win:
                again = pygame.image.load("./images/again3.png")
            else:
                again = pygame.image.load("./images/again1.png")
            again_rect = again.get_rect()
            back = pygame.image.load("./images/return3.png")
            back_rect = back.get_rect()
            if self.is_win:
                end = pygame.image.load("./images/end3.png")
            else:
                end = pygame.image.load("./images/end1.png")
            end_rect = back.get_rect()

            again_rect.centerx = SCREEN_RECT.centerx
            again_rect.y = SCREEN_RECT.height * 0.5
            back_rect.centerx = SCREEN_RECT.centerx
            back_rect.y = SCREEN_RECT.height * 0.8
            end_rect.centerx = SCREEN_RECT.centerx
            end_rect.y = SCREEN_RECT.height * 0.65

            # 让鼠标移至图标切换图片
            if (again_rect.left < mouse_pos[0] < again_rect.right) and (
                            again_rect.top < mouse_pos[1] < again_rect.bottom):
                if self.is_win:
                    again = pygame.image.load("./images/again4.png")
                else:
                    again = pygame.image.load("./images/again2.png")
                if mouse_press[0]:

                    #重置一下未被击落的敌机数
                    EnemyBoss.enemy_die = 0
                    self.is_win = True
                    Game.clicks()
                    Game().start_game()

            if (back_rect.left < mouse_pos[0] < back_rect.right) and (
                            back_rect.top < mouse_pos[1] < back_rect.bottom):
                back = pygame.image.load("./images/return4.png")
                if mouse_press[0]:
                    Game.clicks()
                    main.MainMenu().update_menu()

            if (end_rect.left < mouse_pos[0] < end_rect.right) and (
                            end_rect.top < mouse_pos[1] < end_rect.bottom):
                if self.is_win:
                    end = pygame.image.load("./images/end4.png")
                else:
                    end = pygame.image.load("./images/end2.png")
                if mouse_press[0]:
                    Game.clicks()
                    Game.__game_over()

            self.screen.blit(image, rect)

            if not victory:
                self.print_text(85, SCREEN_RECT.height * 0.2, "\n\n英雄阵亡".format(self.score),
                                color=(255, 0, 0), font=2)
                self.print_text(85, SCREEN_RECT.height * 0.3, "\n你还有梦想吗", color=(255, 0, 0), font=2)
            elif victory:
                if self.score > 3:
                    self.print_text(85, SCREEN_RECT.height * 0.1, "\n成功击败boss".format(self.score),
                                    color = (255, 0, 0), font = 2)
                    self.print_text(40, SCREEN_RECT.height * 0.2, "无情击落友军飞机{:.0f}架".format(self.score),
                                    color=(255, 0, 0), font=2)
                    self.print_text(95, SCREEN_RECT.height * 0.3, "\n你要变的更强".format(self.score),
                                    color=(255,0,0), font=2)
                else:
                    self.print_text(20, SCREEN_RECT.height * 0.2, "损失友军{:.0f}架，你变强了".format(self.score),
                                    color=(255, 0, 0), font=2)
                    self.print_text(20, SCREEN_RECT.height * 0.3, "你有资格去最后的战场了", color=(255, 0, 0), font=2)

            self.screen.blit(again, again_rect)
            self.screen.blit(back, back_rect)
            self.screen.blit(end, end_rect)
            pygame.display.update()

    #结束游戏
    @staticmethod
    def __game_over():
        """退出游戏"""
        pygame.quit()
        exit()

