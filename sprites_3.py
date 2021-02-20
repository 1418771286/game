import pygame
import random

SCREEN_RECT = pygame.Rect(0, 0, 573, 753)

#英雄初始生命值
HERO_LIFE = 3
#boss初始生命值
BOSS_LIFE = 30
#boss左右移动速度
BOSS_MOVE = 1
#boss初始位置，boss向下速度为2，帧为100
BOSS_DISTANCE = -10000
#队友初始血量
TEAMMATE_LIFE = 2
#每一部敌机帮boss加的血量
BOSS_ADD_LIFE = 3


class GameSprite(pygame.sprite.Sprite):
    """游戏精灵父类"""

    def __init__(self, image_name, speed = [0,0]):

        super().__init__()
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.speed = speed

    def update(self):
        #更新位置
        self.rect = self.rect.move(self.speed)

    @staticmethod
    def image_names(picture_name, count):
        #返回一个多图片列表
        names = []
        for i in range(1, count + 1):
            names.append("./images/" + picture_name + str(i) + ".png")
        return names


class Background(GameSprite):
    """背景精灵类"""

    def __init__(self, is_alt = False):

        super().__init__("./images/background8.png", speed=[0, 1])

        #实现一张图片颠倒连接
        if is_alt:
            image = pygame.image.load("./images/background8.png")
            self.image = pygame.transform.flip(image, False, True)
            self.rect.bottom = 0


    def update(self):
        super().update()
        if self.rect.top >= SCREEN_RECT.height:
            self.rect.bottom = 0


class PlaneSprite(GameSprite):
    """飞机精灵类"""

    def __init__(self, image_names, destroy_names, life, speed = [0, 0]):
        #加载第一张图片
        first_image = image_names[0]
        super().__init__(first_image, speed)

        #存储生存图像的私有列表
        self.__life_images = []
        for file_name in image_names:
            image = pygame.image.load(file_name)
            self.__life_images.append(image)

        #存储爆炸时图片的私有列表
        self.__destroy_images = []
        for file_name in destroy_names:
            image = pygame.image.load(file_name)
            self.__destroy_images.append(image)

        self.life = life                        #飞机生命值
        self.life_images = self.__life_images   #将私有列表赋值给公有列表
        self.show_image_index = 0               #图像索引
        self.is_loop_show = True                #默认图像组可以循环
        self.can_destroied = False              #默认不可以摧毁

    def update(self):
        """实现生存和爆炸图片连续播放"""

        super().update()
        # 转换整形，还可以把小数去掉
        index1 = int(self.show_image_index)
        #计算一下生存图片的数量
        count = len(self.life_images)
        #将索引每次加0.1
        self.show_image_index += 0.1

        #如果可以循环，控制索引在0和图片数之间1%3=1,4%3=1
        if self.is_loop_show:
            self.show_image_index %= count

        #如果不可以循环且当索引到最后一张图片，可以摧毁（索引是从0开始的）
        elif self.show_image_index > count - 1:
            self.show_image_index = count - 1
            self.can_destroied = True

        # 把小数去掉
        index2 = int(self.show_image_index)
        #如果索引变了，则变换图片
        if index1 != index2:
            #image是在GameSprite类的，初始方法中切换图片
            self.image = self.life_images[index2]

    def destroied(self):
        # 把生存图片切换到爆炸时的图片
        self.life_images = self.__destroy_images
        # 从爆炸第一张图片开始播放
        self.show_image_index = 0
        #改为不可以循环
        self.is_loop_show = False

        sound = pygame.mixer.Sound('./music/break.wav')
        sound.set_volume(0.6)
        sound.play()
        sound.fadeout(1000)


class Hero(PlaneSprite):
    """英雄精灵"""

    #默认飞机不能发生冰属性子弹（类属性）
    is_ice = False

    def __init__(self, speed = [0, 0]):

        #调用游戏精灵类的静态方法返回图像列表，再调用父类加载
        image_names = GameSprite.image_names("hero1_" ,2)
        destroy_names = GameSprite.image_names("hero1_boom", 6)
        super().__init__(image_names, destroy_names, HERO_LIFE, speed)

        #设置飞机初始位置
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 120

        #创建子弹精灵组
        self.bullet1_group = pygame.sprite.Group()
        #定义一个变量控制子弹发射间隔
        self.fire_space = 0


    def update(self):

        super().update()

        #超出屏幕检测
        if self.rect.left < SCREEN_RECT.left:
            self.rect.left = SCREEN_RECT.left
        elif self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
        elif self.rect.top < SCREEN_RECT.top:
            self.rect.top = SCREEN_RECT.top
        elif self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

    def fire(self):

        sound = pygame.mixer.Sound('./music/shoot.wav')
        sound.set_volume(0.2)
        sound.play()
        sound.fadeout(500)

        #创建子弹精灵
        bullet1 = Bullet1()

        # 设置子弹位置
        bullet1.rect.bottom = self.rect.top + 10
        bullet1.rect.centerx = self.rect.centerx

        # 将子弹添加到精灵组
        self.bullet1_group.add(bullet1)


class EnemyBoss(PlaneSprite):
    """敌机boss类"""

    #定义一个类属性来记录小敌机没死的数量
    enemy_die = 0

    def __init__(self):
        image_names = GameSprite.image_names("boss1_", 1)
        destroy_names = GameSprite.image_names("boss1_boom", 6)
        super().__init__(image_names, destroy_names, BOSS_LIFE)

        # boss开始的位置
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = BOSS_DISTANCE

        #随机开始方向
        self.direction = random.choice([-BOSS_MOVE, BOSS_MOVE])
        #初始速度向下，距离=频率*速度
        self.speed = [0, 2]

        #创建子弹2精灵组
        self.bullet2_group = pygame.sprite.Group()

    def update(self):

        #boss出场警告声
        if self.rect.bottom == SCREEN_RECT.top - 400:
            sound = pygame.mixer.Sound('./music/warn.wav')
            sound.set_volume(1)
            sound.play()

        #boss出现后停在上方
        if self.rect.top >= SCREEN_RECT.top + 0.5 * self.rect.height:
            self.speed = [self.direction, 0]

        #碰壁后速度翻转
        if self.rect.right >= SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
            self.direction = -BOSS_MOVE
        elif self.rect.left <= SCREEN_RECT.left:
            self.rect.left = SCREEN_RECT.left
            self.direction = BOSS_MOVE

        super().update()

        if self.can_destroied:
            self.kill()

    def fire(self):

        sound = pygame.mixer.Sound('./music/missile1.wav')
        sound.set_volume(0.2)
        sound.play()

        #创建两个子弹精灵
        self.bullet2_1 = Bullet2()
        self.bullet2_2 = Bullet2()

        self.bullet2_1.rect.top = self.rect.bottom - 20
        self.bullet2_2.rect.top = self.rect.bottom - 20

        self.bullet2_1.rect.centerx = self.rect.centerx + 70
        self.bullet2_2.rect.centerx = self.rect.centerx - 70

        self.bullet2_group.add(self.bullet2_1, self.bullet2_2)


class Enemy(PlaneSprite):
    """敌机类"""

    def __init__(self):
        image_names = GameSprite.image_names("enemy1_", 2)
        destroy_names = GameSprite.image_names("enemy1_boom", 6)
        #随机敌机生命值
        life = random.randint(1, 4)
        super().__init__(image_names, destroy_names, life)

        #随机敌机出现的位置
        width = SCREEN_RECT.width - self.rect.width
        self.rect.left = random.randint(0, width)
        self.rect.bottom = 0

        #随机敌机速度
        self.speed = [0, random.uniform(1, 4)]


    def update(self):
        #超出屏幕，删除
        if self.rect.top >= SCREEN_RECT.height:
            self.kill()
            #有一架敌方飞机没击落，boss的血量加一
            EnemyBoss.enemy_die += BOSS_ADD_LIFE

        if self.can_destroied:
            self.kill()

        super().update()


class Teammate(PlaneSprite):
    """队友类"""
    def __init__(self):

        image_names = GameSprite.image_names("hero2_", 1)
        destroy_names = GameSprite.image_names("hero2_boom", 6)
        super().__init__(image_names, destroy_names, TEAMMATE_LIFE)

        width = SCREEN_RECT.width - self.rect.width
        self.rect.left = random.randint(0, width)
        self.rect.bottom = 0
        self.speed = [0, random.uniform(1, 4)]

    def update(self):

        super().update()
        if self.rect.top >= SCREEN_RECT.height:
            self.kill()
        if self.can_destroied:
            self.kill()


class Bullet1(GameSprite):
    """英雄子弹类"""

    def __init__(self):
        #如果子弹为冰属性，用不同的图片
        if Hero.is_ice:
            image_name = "./images/bullet3.png"
        else:
            image_name = "./images/bullet1.png"
        super().__init__(image_name, speed = [0, -4])

    def update(self):
        super().update()
        #超过上边界删除
        if self.rect.bottom < 0:
            self.kill()


class Bullet2(GameSprite):
    """boss子弹类"""

    def __init__(self):

        image_name = "./images/bullet2.png"
        super().__init__(image_name, speed= [0, 2])

    def update(self):
        super().update()
        if self.rect.top > SCREEN_RECT.bottom:
            self.kill()


class Snowflake(GameSprite):
    """雪花类"""
    def __init__(self):
        image_name = "./images/snowflake1_1.png"
        super().__init__(image_name)

        width = SCREEN_RECT.width - self.rect.width
        self.rect.left = random.randint(0, width)
        self.rect.bottom = 0
        self.speed = [0, 2]

    def update(self):
        super().update()
        if self.rect.top >= SCREEN_RECT.height:
            self.kill()


class Flame(GameSprite):
    """火焰类"""

    def __init__(self):
        image_name = "./images/flame1_1.png"
        super().__init__(image_name)

        width = SCREEN_RECT.width - self.rect.width
        self.rect.left = random.randint(0, width)
        self.rect.bottom = 0
        self.speed = [0, 2]

    def update(self):
        super().update()
        if self.rect.top >= SCREEN_RECT.height:
            self.kill()





