import pygame
import main
from sprites_3 import *

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
BOSS_SHOOT = 3000
#创建敌机时间间隔
ENEMY_HAPPEN_TIME = 3500
#创建队友时间间隔
TEAMMATE_HAPPEN = 5000
#创建雪花时间
SNOWFLAKE_HAPPEN = 2500
#创建火焰时间
FLAME_HAPPEN = 3000
#游戏帧数
RATE = 100


class Game(object):
    """主程序"""

    #初始化方法
    def __init__(self, ):
        #背景音乐
        pygame.mixer.init()
        self.music = "./music/play3.mp3"
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        #屏幕大小和标题
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        pygame.display.set_caption("生而为王")

        #设置两种字体
        self.font1 = pygame.font.Font("./font/STXINWEI.TTF", 25)
        self.font2 = pygame.font.Font("./font/STXINWEI.TTF", 50)

        self.clock = pygame.time.Clock()    #设置游戏时钟
        self.hero_speed = 3                 #初始英雄移动速度
        self.score = 0                      #记录友军死亡数
        self.is_win = True                  #判断游戏是否能赢，默认能赢
        self.slowly = False                 #判断雪花击中飞机减速
        self.quickly = False                #判断火焰击中飞机加速

        #调用私有方法
        self.__create_sprites()
        #调用静态私有方法返回历史记录
        self.history_score = Game.__record()
        #调用静态私有方法
        self.__create_event()

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

        #创建敌机时间间隔，第一个参数是事件，第二个参数是时间
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

        #不同的生命值显示不同的图片
        if life == 3:
            blood1 = pygame.image.load("./images/blood1.png")
        elif life == 2:
            blood1 = pygame.image.load("./images/blood2.png")
        elif life == 1:
            blood1 = pygame.image.load("./images/blood3.png")
        else:
            blood1 = pygame.image.load("./images/blood4.png")

        #获取血条位置，设置位置，显示血条
        blood1_rect = blood1.get_rect()
        blood1_rect.right = SCREEN_RECT.right
        blood1_rect.bottom = SCREEN_RECT.height - 10
        self.screen.blit(blood1, blood1_rect)

    #boss血量显示
    def boss_blood(self, life):

        #不同生命值显示不同血量
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

            #调用方法
            self.__event_handler()
            self.__update_sprites()
            self.__collide_check()

            #在屏幕上输出伤亡数
            self.print_text(10, 0, "历史最低伤亡：%s" % self.history_score)

            #输出英雄生命值
            self.hero_blood(self.hero.life)

            #计算boss总血量
            boss_all_life = self.boss.life + EnemyBoss.enemy_die
            if boss_all_life <= 0:
                boss_all_life = 0

            #判断boss是否停在上面
            if self.boss.rect.top >= SCREEN_RECT.top + 0.5 * self.boss.rect.height:
                #调用方法显示血条
                self.boss_blood(boss_all_life)

            #显示血量数显示
            self.print_text(SCREEN_RECT.width - 190, 0,
                            "BOSS生命值×{:.0f}".format(boss_all_life))

            #显示友军伤亡数
            self.print_text(SCREEN_RECT.width - 150, 30,
                            "友军阵亡：{:.0f}".format(self.score))

            #更新屏幕
            pygame.display.update()

    #事件监控
    def __event_handler(self):

        #获取所有按键
        keys_pressed = pygame.key.get_pressed()
        
        #判断是否减速和加速
        if self.slowly and self.hero_speed == 3:
            self.hero_speed = 2
            self.slowly = False
        elif self.slowly and self.hero_speed == 4:
            self.hero_speed = 3
            self.slowly = False
        elif self.slowly and self.hero_speed == 2:
            self.hero_speed = 2
            self.slowly = False
        elif self.quickly and self.hero_speed == 2:
            self.hero_speed = 3
            self.quickly = False
        elif self.quickly and self.hero_speed == 3:
            self.hero_speed = 4
            self.hero.life -= 1
            self.quickly = False
        elif self.quickly and self.hero_speed == 4:
            self.hero_speed = 4
            self.quickly = False
            
        #英雄上下左右控制
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

        #上下左右控制
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

        #子弹发射间隔控制
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

            #火焰出现事件
            if event.type == CREATE_FLAME_EVENT:
                self.flame = Flame()
                self.flame_group.add(self.flame)

            #当boss停在上面时，boss才发射子弹
            if event.type == BOSS_FIRE_EVENT and self.boss.speed[1] == 0:
                self.boss.fire()
                #boss死后清除子弹
                # if len(self.boss_group) == 0:
                #     self.boss.bullet2_group.kill()

    #碰撞检测
    def __collide_check(self):

        #遍历英雄与敌机碰撞事件，返回敌机的列表
        for enemy in pygame.sprite.spritecollide(
                self.hero, self.enemy_group,True):
            #将敌机加入销毁组
            self.destroy_group.add(enemy)
            #将敌机移出敌机组
            self.enemy_group.remove(enemy)
            #调用destroied（）方法播放摧毁图片
            enemy.destroied()
            #英雄生命值减一
            self.hero.life -= 1
            #判断英雄是否牺牲
            if self.hero.life <= 0:
                self.hero.destroied()

        #英雄与队友碰撞
        for teammate in pygame.sprite.spritecollide(
                self.hero, self.teammate_group, True):
            self.destroy_group.add(teammate)
            self.teammate_group.remove(teammate)
            teammate.destroied()
            #敌机爆炸数加一
            self.score += 1
            self.hero.life -= 1
            if self.hero.life <= 0:
                self.hero.destroied()

        # 英雄与boss碰撞
        for boss in pygame.sprite.spritecollide(
                self.hero, self.boss_group, True):
            self.destroy_group.add(boss)
            self.boss_group.remove(boss)
            boss.destroied()
            self.hero.destroied()

        #子弹1和敌机碰撞，返回装有敌机的字典
        enemies = pygame.sprite.groupcollide(
            self.enemy_group, self.hero.bullet1_group, False, True).keys()
        for enemy in enemies:
            #用类名调用类属性，如果英雄是冰属性攻击，敌机速度变慢，生命值减一
            if Hero.is_ice :
                enemy.speed = [0, 1]
                enemy.life -= 1
            #否则，敌机被击中则加速，但生命值减二
            else:
                enemy.speed = [0, 4]
                enemy.life -= 2
            if enemy.life <= 0:
                self.destroy_group.add(enemy)
                self.enemy_group.remove(enemy)
                enemy.destroied()

        #子弹1和队友碰撞
        teammates = pygame.sprite.groupcollide(
            self.teammate_group, self.hero.bullet1_group, False, True).keys()
        for teammate in teammates:
            if Hero.is_ice:
                teammate.speed = [0, 1]
                teammate.life -= 1
            else:
                teammate.speed = [0, 3]
                teammate.life -= 2
            if teammate.life <= 0:
                self.destroy_group.add(teammate)
                self.teammate_group.remove(teammate)
                teammate.destroied()
                self.score += 1

        # 子弹1打boss，先计算boss的总血量
        boss_all_life = self.boss.life + EnemyBoss.enemy_die
        enemy_boss = pygame.sprite.groupcollide(
            self.boss_group, self.hero.bullet1_group, False, True).keys()
        for boss in enemy_boss:
            if Hero.is_ice:
                boss.life -= 1
            else:
                boss.life -= 2
            # 测试时发现要-1血boss才会毁灭，所以将其由0改为1
            if boss_all_life <= 1:
                self.destroy_group.add(boss)
                self.boss_group.remove(boss)
                boss.destroied()

        # 子弹2射中英雄
        for _ in pygame.sprite.spritecollide(
                self.hero, self.boss.bullet2_group, True):
            self.hero.life -= 1
            if self.hero.life <= 0:
                self.hero.destroied()

        # 雪花打中英雄
        for _ in pygame.sprite.spritecollide(
                self.hero, self.snowflake_group, True):
            #加载音效，和背景音乐是不一样的
            sound = pygame.mixer.Sound('./music/ice1.wav')
            sound.set_volume(0.6)
            sound.play()
            sound.fadeout(3000)
            #雪花打中后，英雄减速，子弹变冰属性
            self.slowly = True
            Hero.is_ice = True

        # 火焰打中英雄
        for _ in pygame.sprite.spritecollide(
                self.hero, self.flame_group, True):
            sound = pygame.mixer.Sound('./music/flame2.wav')
            sound.set_volume(0.4)
            sound.play()
            sound.fadeout(1500)
            #火焰打中后，英雄加速，子弹取消冰属性
            self.quickly = True
            Hero.is_ice = False


        #英雄可以销毁就结束游戏
        if self.hero.can_destroied:
            #播放失败音效
            pygame.mixer.music.stop()
            sound = pygame.mixer.Sound('./music/fail1.wav')
            sound.set_volume(0.3)
            sound.play()
            #英雄阵亡，不能赢，
            self.is_win = False
            #调用介绍页面，传入False参数，调用失败时的语句
            Game.over_page(self, False)

        #boss可以销毁且能赢则结束游戏（防止同归于尽boss先死）
        elif self.boss.can_destroied and self.is_win == True:
            #分数小于10才记录
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
        #选择字体
        if font == 1:
            imgText1 = self.font1.render(self.text, True, color)
            self.screen.blit(imgText1, (x, y))
        if font == 2:
            imgText2 = self.font2.render(self.text, True, color)
            self.screen.blit(imgText2, (x, y))

    #历史记录
    @staticmethod
    def __record():
        #只读方式打开
        file = open("./text/c3.txt", "r")
        text = file.read()
        file.close()
        if len(text) == 0:
            return "无"
        else:
            return chr(int(text))

    #更新记录
    def update_record(self):
        #只读方式打开
        file = open("./text/c3.txt", "r")
        text = file.read()
        file.close()
        #如果无记录，直接写入该次得分
        if len(text) == 0:
            #加密
            encrypt = ord("{}".format(self.score))
            #覆盖写的方式打开
            file = open("./text/c3.txt", "w")
            file.write(str(encrypt))
            file.close()
        #有记录则判断哪个记录小就要哪个
        else :
            decrypt = chr(int(text))
            if self.score < int(decrypt):
                decrypt = self.score
                encrypt = ord("{}".format(decrypt))
                file = open("./text/c3.txt", "w")
                file.write(str(encrypt))
                file.close()

    #更新精灵组
    def __update_sprites(self):
        #遍历每个精灵组
        for group in [self.back_group, self.hero_group,
                      self.enemy_group, self.destroy_group,
                      self.hero.bullet1_group, self.teammate_group,
                      self.boss_group, self.boss.bullet2_group,
                      self.snowflake_group, self.flame_group]:
            #更新精灵组
            group.update()
            #显示精灵组
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

            back = pygame.image.load("./images/return3.png")
            image = pygame.image.load("./images/background1.png")
            # 判断是否可赢，加载不同的页面
            if self.is_win:
                end = pygame.image.load("./images/end3.png")
            else:
                end = pygame.image.load("./images/end1.png")
            #判断是否可赢，加载不同的页面
            if self.is_win:
                again = pygame.image.load("./images/again3.png")
            else:
                again = pygame.image.load("./images/again1.png")

            #获取位置
            rect = image.get_rect()
            again_rect = again.get_rect()
            back_rect = back.get_rect()
            end_rect = back.get_rect()

            #位置控制
            again_rect.centerx = SCREEN_RECT.centerx
            again_rect.y = SCREEN_RECT.height * 0.5
            back_rect.centerx = SCREEN_RECT.centerx
            back_rect.y = SCREEN_RECT.height * 0.8
            end_rect.centerx = SCREEN_RECT.centerx
            end_rect.y = SCREEN_RECT.height * 0.65

            # 重新开始游戏
            if (again_rect.left < mouse_pos[0] < again_rect.right) and (
                            again_rect.top < mouse_pos[1] < again_rect.bottom):
                if self.is_win:
                    again = pygame.image.load("./images/again4.png")
                else:
                    again = pygame.image.load("./images/again2.png")
                if mouse_press[0]:
                    #重置一下未被击落的敌机数
                    EnemyBoss.enemy_die = 0
                    #让是否能赢，刷新回初始能赢
                    self.is_win = True
                    #播放鼠标声
                    Game.clicks()
                    Game().start_game()

            #返回主菜单
            if (back_rect.left < mouse_pos[0] < back_rect.right) and (
                            back_rect.top < mouse_pos[1] < back_rect.bottom):
                back = pygame.image.load("./images/return4.png")
                if mouse_press[0]:
                    Game.clicks()
                    main.MainMenu().update_menu()

            #游戏结束
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
                self.print_text(40, SCREEN_RECT.height * 0.2, "包括你一共阵亡了{}人".format((self.score+1)),
                                color=(255, 0, 0), font=2)
                self.print_text(80, SCREEN_RECT.height * 0.3, "或许这里不适合你", color=(255, 0, 0), font=2)
            elif victory:
                if self.score > 3:
                    self.print_text(5, SCREEN_RECT.height * 0.1, "{}名队友的牺牲换来了胜利".format(self.score),
                                    color = (255, 0, 0), font = 2)
                    self.print_text(80, SCREEN_RECT.height * 0.2, "强者才能保护队友".format(self.score),
                                    color=(255, 0, 0), font=2)
                    self.print_text(105, SCREEN_RECT.height * 0.3, "\n你还不够强".format(self.score),
                                    color=(255,0,0), font=2)
                elif self.score == 0:
                    self.print_text(15, SCREEN_RECT.height * 0.2, "没想到还有英雄能零伤亡",
                                    color=(255, 0, 0), font=2)
                    self.print_text(15, SCREEN_RECT.height * 0.3, "游戏开发者对你表示服气", color=(255, 0, 0), font=2)
                else:
                    self.print_text(15, SCREEN_RECT.height * 0.2, "恭喜你，低伤亡击败boss",
                                    color=(255, 0, 0), font=2)
                    self.print_text(50, SCREEN_RECT.height * 0.3, "获得“英雄王”称号", color=(255, 0, 0), font=2)

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

