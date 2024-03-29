

import pygame
import os
import random
import csv


pygame.init() #initializing pygame

screen_width=800
screen_height= int(screen_width * 0.8 )  

screen= pygame.display.set_mode((screen_width,screen_height))      #screen display size
pygame.display.set_caption('SHOOTER')         #caption name

#set framerate
clock= pygame.time.Clock()
FPS=60

#define game variables
GRAVITY=0.698
SCROLL_THRESH = 200  #dist b/w player and screen from where screen will scroll
ROWS=16
COLS=150 
TILE_SIZE= screen_height//ROWS
TILE_TYPES= 21
level=1
screen_scroll =0
bg_scroll =0
start_game = False
MAX_LEVEL = 3

#defining actions variables
moving_left=False 
moving_right=False 
shoot=False


#load images

#loading bg images
pine1_img= pygame.image.load('assets/img/background/pine1.png') 
pine2_img= pygame.image.load('assets/img/background/pine2.png') 
mountain_img= pygame.image.load('assets/img/background/mountain.png') 
sky_img= pygame.image.load('assets/img/background/sky_cloud.png') 

#button images
start_img= pygame.image.load('assets/img/start_btn.png') 
restart_img= pygame.image.load('assets/img/restart_btn.png') 
exit_img= pygame.image.load('assets/img/exit_btn.png') 


#loading bullet
bullet_img= pygame.image.load('assets/img/icons/bullet.png') #bullet
health_img= pygame.image.load('assets/img/icons/health.png') #health bar


#store tiles in a list
img_list=[]
for x in range(TILE_TYPES):
    img = pygame.image.load(f'assets/img/tile/{x}.png')
    img = pygame.transform.scale(img , (TILE_SIZE,TILE_SIZE))
    img_list.append(img)




#pickup items
heal_box_img = pygame.image.load('assets/img/icons/health_box.png')
heal_box_img = pygame.transform.scale(heal_box_img,(int(heal_box_img.get_width()*0.6) , int(heal_box_img.get_height()*0.6)))  #scalling health box

ammo_box_img = pygame.image.load('assets/img/icons/ammo_box.png')
ammo_box_img = pygame.transform.scale(ammo_box_img,(int(ammo_box_img.get_width()*0.6) , int(ammo_box_img.get_height()*0.6)))



item_boxes = {
        'health': heal_box_img , 'ammo':ammo_box_img     
}

  
#define colours
BG='#CDF0FF'
# BG=(205,240,255)  another way of specifying
WHITE=(255,255,255)
DENIM = '#0872A0'
GREEN=(34,139,34)
RED=(255,0,0)
BLACK=(0,0,0)

#define font
font = pygame.font.SysFont("roboto" , 15)

def draw_text(text,font,text_col,x,y):
    img= font.render(text, True , text_col)
    screen.blit(img,(x,y))




def draw_bg():
    screen.fill(BG)
    width= sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img , ( (x * width) - bg_scroll * 0.5,0))

        screen.blit(mountain_img , ( (x * width) - bg_scroll * 0.6,screen_height - mountain_img.get_height() - 290 ))

        screen.blit(pine1_img , ( (x * width)- bg_scroll * 0.7,screen_height - pine1_img.get_height() - 140 ))

        screen.blit(pine2_img , ( (x * width) - bg_scroll * 0.8,screen_height - pine2_img.get_height() ))
        #pygame.draw.line(screen, DENIM, (0,300), (screen_width,300))


#funtion to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    exit_group.empty()
    water_group.empty()  

    #create empty tile list
    data=[]
    for row in range(ROWS):
        r=[-1] * COLS  #list with 150s -1 in it
        data.append(r) #40 rows with entry -1
            
    return data    



class soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive=True
        self.char_type=char_type
        self.speed=speed
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.ammo = ammo
        self.start_ammo = ammo
        self.direction=1
        self.jump= False
        self.in_air=False
        self.vel_y=0
        self.flip=False
        self.animate_list=[]
        self.index=0
        self.frame_index=0
        self.action=0
        self.update_time = pygame.time.get_ticks()
        
        #create ai sepcific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0,150,20)
        self.idling = False
        self.idling_counter=0

        #loading all images 
        animation_types=['Idle','Run','Jump','Death']
        for animation in animation_types:
            temp_list=[]

            num_of_frames =  len(os.listdir(f'assets/img/{self.char_type}/{animation}'))      #counting no of images in each folder

            for i in range(num_of_frames):

                img=pygame.image.load(f'assets/img/{self.char_type}/{animation}/{i}.png')                           #to load the image to pygame

                img = pygame.transform.scale(img,(int(img.get_width()*scale) , int(img.get_height()*scale)))  #changing size of player1

                temp_list.append(img)
            
            self.animate_list.append(temp_list)
#at index 0, animate_list has idle images and at index 1 it has running images, 2 for jump images , 3 for death
        




        self.img= self.animate_list[self.action][self.index]    
        self.rect = self.img.get_rect()        #create a rect boundary box around image, helps in movement also collison
        self.rect.center=(x,y)
        self.width = self.img.get_width()
        self.height = self.img.get_height()


    def update(self):
        self.update_animation()
        self.check_alive()
        #updating shoot cooldown
        if self.shoot_cooldown>0:
            self.shoot_cooldown -= 1



    def move(self, moving_left,moving_right):
        #reset movement variables
        dx=0
        dy=0
        screen_scroll = 0
        #assign movemnet variable if moving left or right
        if moving_left:
            dx= -self.speed
            self.flip=True
            self.direction= -1
            
            
        if moving_right:   
            dx= +self.speed
            self.flip=False
            self.direction= 1

        if self.jump==True and self.in_air == False:   
            self.vel_y= -11
            self.jump=False
            self.in_air=True

        #applying gravity
        self.vel_y += GRAVITY   
        if self.vel_y > 10:
            self.vel_y

        dy += self.vel_y

        #check for collison
        for tile in world.obstacle_list:
            #check collison in x direction
            if tile[1].colliderect(self.rect.x + dx , self.rect.y , self.width , self.height):
                dx = 0  #this stops player to move once collison occurs

                #if ai i.e. enemy hit the wall then make it turn
                # if self.char_type == 'enemy':
                #     self.direction *= -1
                #     self.move_counter = 0
            

            #check collison in y direction
            if tile[1].colliderect(self.rect.x , self.rect.y + dy , self.width , self.height):
                #check if below the ground ie jumping
                if self.vel_y<0:   #player moving up 
                    self.vel_y=0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground ie falling
                elif self.vel_y>= 0:   #player moving up 
                    self.vel_y=0
                    self.in_air= False
                    dy = tile[1].top - self.rect.bottom
                
        #checking collison with water
        if pygame.sprite.spritecollide(self , water_group , False):
            self.health=0


        #check collison with exit 
        level_complete = False    
        if pygame.sprite.spritecollide(self , exit_group , False):
            level_complete = True



        #check if player falls off
        if self.rect.bottom > screen_height:
            self.health=0


        #checking if player is going off the edges of screen
        if self.char_type == 'player' : 
             if self.rect.left + dx <0 or self.rect.right + dx > screen_width :
                 dx =0        


        #updating rect position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll based on player postion
        if self.char_type == 'player' :
            if (self.rect.right > screen_width - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - screen_width) \
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)) :
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll , level_complete

    def shoot(self):
        if self.shoot_cooldown==0 and self.ammo > 0:
            self.shoot_cooldown=20
            bullet=Bullet(self.rect.centerx +(0.75*self.rect.size[0]* self.direction),self.rect.centery,self.direction)

            bullet_group.add(bullet)
            
            self.ammo -= 1  #reducing ammo

    def ai(self):
        if self.alive and player.alive:
            if self.idling==False and random.randint(1,200) == 1:
                self.update_action(0) #0 for idle
                self.idling=True
                self.idling_counter=50

            #check if vision rect collides with player's rect
            if self.vision.colliderect(player.rect):
                self.update_action(0) #stop and start shooting , 0 for stop
                self.shoot()   #starts to shoot
                self.speed=0

            else:
                if self.idling==False:

                    if self.direction==1:
                        ai_moving_right =True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right

                    self.move(ai_moving_left , ai_moving_right)   
                    self.update_action(1) #1 for run  
                    self.move_counter += 1

                    #update ai vision as enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction , self.rect.centery ) 
                    #pygame.draw.rect(screen,WHITE,self.vision) #we can watch the ai vision rect through this

                    if(self.move_counter > TILE_SIZE):
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter<=0:
                        self.idling=False

        #scroll
        self.rect.x += screen_scroll        

             
    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN=100

        #update image depending on current frame
        self.img= self.animate_list[self.action][self.frame_index]    


        #check if enough time ha spassec since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.update_time=pygame.time.get_ticks()
                self.frame_index += 1
        #if animation has run out the reset back to start
        if self.frame_index>=len(self.animate_list[self.action]):
                if self.action == 3:        # 3 -> death
                    self.frame_index= len(self.animate_list[self.action])-1
                else :
                    self.frame_index=0


    def update_action(self,new_action):
            if new_action != self.action:
                 self.action= new_action

                 #updating the animation settings
                 self.frame_index=0
                 self.update_time=pygame.time.get_ticks()
                

    def check_alive(self):
        if self.health<=0:
            self.health=0
            self.speed=0
            self.alive=False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.img, self.flip , False),self.rect) 
        #blit function - to place image onto the screen and pygame.transform.flip(Surface, xbool, ybool)


class World():
    def __init__(self):
       self.obstacle_list = []

    def process_data(self,data):     #to process the csv file

        self.level_length = len(data[0])  #to count no of columns
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x,tile in enumerate(row):
                if(tile>=0):
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    
                    if tile >= 0 and tile <= 8:  #earth
                        self.obstacle_list.append(tile_data)

                    elif tile >= 9 and tile <= 10 :
                        water = Water(img,x* TILE_SIZE,y * TILE_SIZE)
                        water_group.add(water)   

                    elif tile >= 11 and tile <=14:  #decorative elements
                        decoration = Decoration(img,x* TILE_SIZE,y * TILE_SIZE)
                        decoration_group.add(decoration)

                    elif tile == 15: #create player
                        player=soldier('player',x*TILE_SIZE,y*TILE_SIZE
                                       ,1.65,5,20)
                        health_bar= healthbar(10,10, player.health, player.health)

                    elif tile==16: #create enemies
                        enemy=soldier('enemy',x*TILE_SIZE,y*TILE_SIZE ,1.65,2,20) 
                        enemy_group.add(enemy)
                    
                    #temp - create item boxes
                    elif tile ==  17 : #create ammo box
                        item_box = Itembox('ammo',x* TILE_SIZE,y * TILE_SIZE)
                        item_box_group.add(item_box)
                    
                    # 18 is for grenade but currently we are implementing grenade option
                        
                    elif tile ==  19 : #create ammo box
                        item_box = Itembox('health',x* TILE_SIZE,y * TILE_SIZE)
                        item_box_group.add(item_box)

                    elif tile==20 : #create exit
                        exit = Exit(img,x* TILE_SIZE,y * TILE_SIZE)
                        exit_group.add(exit)   
        
        

        return player , health_bar          
 
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0] , tile[1])  #tile[0] is for image and tile[1] is for rect coordinates




class Decoration(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
         pygame.sprite.Sprite.__init__(self)
         self.image = img
         self.rect = self.image.get_rect()
         self.rect.midtop = (x + TILE_SIZE//2 , y+ (TILE_SIZE - self. image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
         pygame.sprite.Sprite.__init__(self)
         self.image = img
         self.rect = self.image.get_rect()
         self.rect.midtop = (x + TILE_SIZE//2 , y+ (TILE_SIZE - self. image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
         pygame.sprite.Sprite.__init__(self)
         self.image = img
         self.rect = self.image.get_rect()
         self.rect.midtop = (x + TILE_SIZE//2 , y+ (TILE_SIZE - self. image.get_height()))

    def update(self):
        self.rect.x += screen_scroll




class Itembox(pygame.sprite.Sprite):
     def __init__(self,item_type,x,y):
         pygame.sprite.Sprite.__init__(self)
         self.item_type = item_type
         self.image = item_boxes[self.item_type]
         self.rect = self.image.get_rect()
         self.rect.midtop = (x + TILE_SIZE//2 , y + (TILE_SIZE - self.image.get_height()))
     def update(self):
         #scroll
         self.rect.x += screen_scroll
         if pygame.sprite.collide_rect(self,player):
            if self.item_type=='health':
                player.health += 40
                self.kill()
                if player.health > player.max_health :
                    player.health=player.max_health
                   
            else :
                player.ammo += 20
                self.kill()

        


class healthbar():
    def __init__(self,x,y,health,max_health):
        self.x=x
        self.y=y
        self.health=health
        self.max_health=max_health
    def draw(self,health):
        self.health=health
        #health ratio
        ratio = self.health/ self.max_health

        pygame.draw.rect(screen,WHITE ,(self.x -2,self.y -2,154 ,24))
        pygame.draw.rect(screen,RED ,(self.x,self.y,150,20))
        pygame.draw.rect(screen,GREEN ,(self.x,self.y,150* ratio ,20))







class Bullet(pygame.sprite.Sprite):
     def __init__(self,x,y,direction):
         pygame.sprite.Sprite.__init__(self)
         self.speed=10
         self.image=bullet_img
         self.rect=self.image.get_rect()
         self.rect.center=(x,y)
         self.direction= direction

     def update(self):
         #move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll

         #check if bullet has gone off screen
        if(self.rect.right <0 or self.rect.left >screen_width):
             self.kill()

        #check with collison with level
        for tile in world.obstacle_list :
            if tile[1].colliderect(self.rect):     
                self.kill()     

         #check collison with character
        if pygame.sprite.spritecollide(player, bullet_group , False):
            if player.alive:
                player.health -= 10
                self.kill()  

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group , False):
                if enemy.alive:
                    enemy.health -= 30
                    
                    self.kill()         

#button class
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create buttons
start_button = Button(screen_width//2 - 130 , screen_height//2 -150 , start_img , 1)                        
exit_button = Button(screen_width//2 - 110 , screen_height//2 + 50 , exit_img , 1)                        
restart_button = Button(screen_width//2 - 100 , screen_height//2 - 50 , restart_img , 2)                        





#create sprite group
bullet_group= pygame.sprite.Group()         
enemy_group= pygame.sprite.Group()   
item_box_group = pygame.sprite.Group()      
decoration_group = pygame.sprite.Group()      
water_group = pygame.sprite.Group()      
exit_group = pygame.sprite.Group()      










#create empty tile list
world_data=[]
for row in range(ROWS):
    r=[-1] * COLS  #list with 150s -1 in it
    world_data.append(r) #40 rows with entry -1

#load level data and create world
with open(f'assets/level{level}_data.csv' , newline='') as csvfile:    #cmd to open csv file
    reader = csv.reader(csvfile , delimiter=',')
    for x, row in enumerate(reader) :
        for y , tile in enumerate(row):    #y keeps the count of enteries 
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)


run=True 

while run :
    

    clock.tick(FPS)

    if start_game == False:
        #draw main menu
        screen.fill(DENIM)
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
        
    else:
        #update bg
        draw_bg()
        
        #draw world map
        world.draw()

        #show player health
        health_bar.draw( player.health )

        #show ammo and health
        #draw_text('Ammo :', font,WHITE,7,35)
        for x in range(player.ammo):
            screen.blit(bullet_img , (10 +(x*10),40))
        #draw_text(f'Health:{player.health} ', font,WHITE,7,35)
        


        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #update and draw groups
        bullet_group.update()
        bullet_group.draw(screen)
    
        item_box_group.update()
        item_box_group.draw(screen)

        decoration_group.update()
        decoration_group.draw(screen)

        water_group.update()
        water_group.draw(screen)

        exit_group.update()
        exit_group.draw(screen)
    





        if player.alive:

            #shoot bulllet
            if shoot:
                player.shoot()

        

            elif player.in_air:
                player.update_action(2) #2 means jump
            elif moving_left or moving_right:
                player.update_action(1)  #1 means run
            else:
                player.update_action(0) #0 for idle 

            screen_scroll , level_complete = player.move(moving_left,moving_right)
            bg_scroll -= screen_scroll

            #check if player the complete the level

            if level_complete:
                level += 1
                bg_scroll=0
                world_data = reset_level()
                if level <= MAX_LEVEL :
                    #load level data and create world
                    with open(f'assets/level{level}_data.csv' , newline='') as csvfile:    #cmd to open csv file
                        reader = csv.reader(csvfile , delimiter=',')
                        for x, row in enumerate(reader) :
                            for y , tile in enumerate(row):    #y keeps the count of enteries 
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)



        else:
            screen_scroll=0
            if restart_button.draw(screen):
                bg_scroll=0
                world_data = reset_level()

                #load level data and create world
                with open(f'assets/level{level}_data.csv' , newline='') as csvfile:    #cmd to open csv file
                    reader = csv.reader(csvfile , delimiter=',')
                    for x, row in enumerate(reader) :
                        for y , tile in enumerate(row):    #y keeps the count of enteries 
                            world_data[x][y] = int(tile)

                world = World()
                player, health_bar = world.process_data(world_data)



     
        

    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT: #when someone presses red cross button 
            run=False

        #keyboard presses
                
        if event.type == pygame.KEYDOWN:
            if event.key== pygame.K_a:
                moving_left=True
            if event.key== pygame.K_d:
                moving_right=True
            if event.key== pygame.K_w and player.alive:
                player.jump=True               
            if event.key== pygame.K_SPACE:
                shoot=True               
            if event.key == pygame.K_ESCAPE:
                run=False         

        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key== pygame.K_a:
                moving_left=False
            if event.key== pygame.K_d:
                moving_right=False             
            if event.key== pygame.K_SPACE:
                shoot=False    



    pygame.display.update()    #this updates the screen 

pygame.quit()
