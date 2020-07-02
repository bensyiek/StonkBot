import requests, pickle
import time, datetime, re
import math
import threading
import matplotlib.pyplot as plot
from scipy.stats import norm
import nbt, base64, io

import discord, asyncio, os
from discord.ext import commands
from dotenv import load_dotenv

import item_map

#weighting_base = 2

def find_image(name):
    if '[lvl' in name.lower():
        name = re.sub(r'\[lvl [0-9]+\] ','',name.lower()) + ' Pet'
    elif 'potion' in name.lower():
        return 'Water_Bottle.webp'
    elif 'rune' in name.lower():
        name = re.sub(r' [i]+','',name.lower())
    elif 'crab hat' in name.lower():
        return 'Crab_Hat.webp'
    elif 'travel scroll' in name.lower():
        return 'Empty_Map.webp'
    name = ' '.join(name.split('_'))
    adj_name = '_'.join([word[0:1].upper()+word[1:].lower() for word in name.split(' ')])
    if adj_name in item_map.item_map:
        adj_name = item_map.item_map[adj_name]
    return adj_name+'.webp' if adj_name+'.webp' in os.listdir('assets/icons/') else 'Default.png'

class ah_item:
    def __init__(self,name,tier,category,reforge,metadata=set(),enchantments={}):
        self.name = name
        self.metadata = metadata
        self.tier = tier
        self.category = category
        self.reforge = reforge
        self.enchantments = enchantments
    def __repr__(self):
        if self.reforge:
            return self.reforge + ' ' + self.name
        else:
            return self.name
    def __str__(self):
        if self.reforge:
            return self.reforge + ' ' + self.name
        else:
            return self.name
    def __eq__(self,obj):
        if type(obj) != ah_item:
            return False
        if obj.name != self.name:
            return False
        elif obj.metadata != self.metadata:
            return False
        elif obj.reforge != self.reforge:
            return False
        elif obj.enchantments != self.enchantments:
            return False
        elif obj.tier != self.tier:
            return False
        return True
    def __ne__(self,obj):
        return not self.__eq__(obj)
    def __hash__(self):
        return hash(hash(''.join(self.metadata))+hash(self.reforge)+hash(self.name))

class hypixel_api:

    echo = False ##for debug

    bazaar_items = ['BROWN_MUSHROOM', 'INK_SACK:3', 'INK_SACK:4', 'TARANTULA_WEB', 'CARROT_ITEM', 'ENCHANTED_POTATO', 'ENCHANTED_SLIME_BALL', 'ENCHANTED_GOLDEN_CARROT', 'ENCHANTED_RED_MUSHROOM', 'ENCHANTED_RABBIT_HIDE', 'ENCHANTED_BIRCH_LOG', 'ENCHANTED_GUNPOWDER', 'ENCHANTED_MELON', 'ENCHANTED_SUGAR', 'CACTUS', 'ENCHANTED_BLAZE_ROD', 'ENCHANTED_CAKE', 'PUMPKIN', 'ENCHANTED_BROWN_MUSHROOM', 'WHEAT', 'ENCHANTED_RAW_SALMON', 'ENCHANTED_GLISTERING_MELON', 'PRISMARINE_SHARD', 'PROTECTOR_FRAGMENT', 'ENCHANTED_EMERALD', 'ENCHANTED_SPIDER_EYE', 'RED_MUSHROOM', 'MUTTON', 'ENCHANTED_MELON_BLOCK', 'WISE_FRAGMENT', 'DIAMOND', 'COBBLESTONE', 'SPIDER_EYE', 'RAW_FISH', 'ENCHANTED_PUFFERFISH', 'POTATO_ITEM', 'ENCHANTED_HUGE_MUSHROOM_1', 'ENCHANTED_COBBLESTONE', 'ENCHANTED_HUGE_MUSHROOM_2', 'PORK', 'PRISMARINE_CRYSTALS', 'ICE', 'HUGE_MUSHROOM_1', 'HUGE_MUSHROOM_2', 'ICE_BAIT', 'LOG_2:1', 'ENCHANTED_SNOW_BLOCK', 'GOLDEN_TOOTH', 'STRING', 'RABBIT_FOOT', 'REDSTONE', 'ENCHANTED_CACTUS_GREEN', 'ENCHANTED_LAPIS_LAZULI_BLOCK', 'ENCHANTED_ENDSTONE', 'ENCHANTED_COOKIE', 'ENCHANTED_SAND', 'ENCHANTED_STRING', 'STRONG_FRAGMENT', 'SLIME_BALL', 'SNOW_BALL', 'ENCHANTED_ACACIA_LOG', 'ENCHANTED_EGG', 'SAND', 'RAW_CHICKEN', 'ENCHANTED_LAPIS_LAZULI', 'ENCHANTED_GHAST_TEAR', 'ENCHANTED_COCOA', 'CARROT_BAIT', 'SEEDS', 'ENCHANTED_LEATHER', 'ENCHANTED_SPONGE', 'HAY_BLOCK', 'INK_SACK', 'FLINT', 'ENCHANTED_ROTTEN_FLESH', 'ENCHANTED_SPRUCE_LOG', 'WOLF_TOOTH', 'ENCHANTED_GRILLED_PORK', 'ENCHANTED_NETHER_STALK', 'ENCHANTED_REDSTONE_BLOCK', 'ENCHANTED_QUARTZ_BLOCK', 'GREEN_CANDY', 'ENCHANTED_REDSTONE', 'ENCHANTED_REDSTONE_LAMP', 'GRAVEL', 'MELON', 'ENCHANTED_LAVA_BUCKET', 'ENCHANTED_PACKED_ICE', 'RAW_FISH:3', 'ENCHANTED_PRISMARINE_SHARD', 'ENCHANTED_IRON_BLOCK', 'ENCHANTED_CARROT_STICK', 'BONE', 'RAW_FISH:2', 'RAW_FISH:1', 'REVENANT_FLESH', 'ENCHANTED_GLOWSTONE', 'ENCHANTED_PORK', 'FEATHER', 'NETHERRACK', 'WHALE_BAIT', 'SPONGE', 'BLAZE_ROD', 'ENCHANTED_DARK_OAK_LOG', 'YOUNG_FRAGMENT', 'ENCHANTED_CLOWNFISH', 'ENCHANTED_GOLD', 'ENCHANTED_RAW_CHICKEN', 'ENCHANTED_WATER_LILY', 'LOG:1', 'CATALYST', 'LOG:3', 'LOG:2', 'BLESSED_BAIT', 'ENCHANTED_GLOWSTONE_DUST', 'ENCHANTED_INK_SACK', 'ENCHANTED_CACTUS', 'ENCHANTED_SUGAR_CANE', 'ENCHANTED_COOKED_SALMON', 'ENCHANTED_SEEDS', 'LOG', 'GHAST_TEAR', 'UNSTABLE_FRAGMENT', 'ENCHANTED_ENDER_PEARL', 'PURPLE_CANDY', 'ENCHANTED_FERMENTED_SPIDER_EYE', 'SPIKED_BAIT', 'ENCHANTED_GOLD_BLOCK', 'ENCHANTED_JUNGLE_LOG', 'ENCHANTED_FLINT', 'IRON_INGOT', 'ENCHANTED_EMERALD_BLOCK', 'ENCHANTED_CLAY_BALL', 'GLOWSTONE_DUST', 'GOLD_INGOT', 'REVENANT_VISCERA', 'TARANTULA_SILK', 'ENCHANTED_MUTTON', 'SUPER_COMPACTOR_3000', 'SUPER_EGG', 'ENCHANTED_IRON', 'STOCK_OF_STONKS', 'ENCHANTED_HAY_BLOCK', 'ENCHANTED_BONE', 'ENCHANTED_PAPER', 'ENCHANTED_DIAMOND_BLOCK', 'SPOOKY_BAIT', 'SUPERIOR_FRAGMENT', 'EMERALD', 'ENCHANTED_RABBIT_FOOT', 'LIGHT_BAIT', 'HOT_POTATO_BOOK', 'ENCHANTED_ICE', 'CLAY_BALL', 'OLD_FRAGMENT', 'GREEN_GIFT', 'PACKED_ICE', 'WATER_LILY', 'HAMSTER_WHEEL', 'LOG_2', 'ENCHANTED_OBSIDIAN', 'ENCHANTED_COAL', 'COAL', 'ENCHANTED_QUARTZ', 'ENCHANTED_COAL_BLOCK', 'ENDER_PEARL', 'ENCHANTED_PRISMARINE_CRYSTALS', 'ENCHANTED_WET_SPONGE', 'ENCHANTED_RAW_FISH', 'ENDER_STONE', 'FOUL_FLESH', 'QUARTZ', 'RAW_BEEF', 'ENCHANTED_EYE_OF_ENDER', 'MAGMA_CREAM', 'SUGAR_CANE', 'RED_GIFT', 'ENCHANTED_RAW_BEEF', 'ENCHANTED_SLIME_BLOCK', 'ENCHANTED_FEATHER', 'ENCHANTED_OAK_LOG', 'RABBIT_HIDE', 'WHITE_GIFT', 'RABBIT', 'SULPHUR', 'NETHER_STALK', 'DARK_BAIT', 'ENCHANTED_CARROT', 'ENCHANTED_PUMPKIN', 'ROTTEN_FLESH', 'ENCHANTED_COOKED_FISH', 'OBSIDIAN', 'MINNOW_BAIT', 'ENCHANTED_MAGMA_CREAM', 'ENCHANTED_FIREWORK_ROCKET', 'LEATHER', 'ENCHANTED_COOKED_MUTTON', 'ENCHANTED_RABBIT', 'ENCHANTED_BREAD', 'ENCHANTED_CHARCOAL', 'ENCHANTED_BLAZE_POWDER', 'SUMMONING_EYE', 'FISH_BAIT', 'SNOW_BLOCK', 'ENCHANTED_BAKED_POTATO', 'COMPACTOR', 'ENCHANTED_DIAMOND']
    sig_level = 0.01
    database_locked = False
    
    API_KEY = '' ##Key removed for GitHub publication 
    web = 'https://api.hypixel.net/'
    very_regular = ['DIAMOND','REDSTONE','QUARTZ','MELON','COAL','EMERALD',]
    regular = ['OBSIDIAN','COBBLESTONE','SPIDER_EYE','SLIME_BALL','RED_MUSHROOM',
               'PUMPKIN','BROWN_MUSHROOM','MUTTON','RAW_FISH','PORK','STRING',
               'SAND','BONE','SPONGE','GHAST_TEAR','FLINT','CLAY_BALL','ENDER_PEARL','FEATHER',
               'GLOWSTONE_DUST','ICE','MAGMA_CREAM','PRISMARINE_SHARD','PRISMARINE_CRYSTALS','RABBIT','RABBIT_FOOT',
               'RAW_BEEF','RAW_CHICKEN','WATER_LILY','ROTTEN_FLESH',]
                ##gunpowder?? 'CLOWNFISH'??? logs???
    up_crafts = {
        'ENCHANTED_'+item : [(item,160)] for item in regular+very_regular
        }
    up_crafts.update({
        'ENCHANTED_' + item + '_BLOCK' : [('ENCHANTED_'+item,160)] for item in very_regular
        })
    up_crafts.update({
        'COMPACTOR'                         : [('ENCHANTED_COBBLESTONE',8),('ENCHANTED_REDSTONE',1)],
        'ENCHANTED_BAKED_POTATO'            : [('ENCHANTED_POTATO',160)],
        'ENCHANTED_BLAZE_POWDER'            : [('BLAZE_ROD',160)],
        'ENCHANTED_BLAZE_ROD'               : [('ENCHANTED_BLAZE_POWDER',160)],
        'ENCHANTED_CACTUS_GREEN'            : [('CACTUS',160)],
        'ENCHANTED_CAKE'                    : [('WHEAT',3),('ENCHANTED_SUGAR',2),('ENCHANTED_EGG',1)],
        'ENCHANTED_CARROT_STICK'            : [('ENCHANTED_CARROT',64)],
        'ENCHANTED_COOKED_FISH'             : [('ENCHANTED_RAW_FISH',160)],
        'ENCHANTED_COOKED_MUTTON'           : [('ENCHANTED_MUTTON',160)],
        'ENCHANTED_COOKED_SALMON'           : [('ENCHANTED_RAW_SALMON',160)],
        'ENCHANTED_COOKIE'                  : [('ENCHANTED_COCOA',128),('WHEAT',32)],
        'ENCHANTED_ENDSTONE'                : [('ENDER_STONE',160)],
        'ENCHANTED_EYE_OF_ENDER'            : [('BLAZE_ROD',32),('ENCHANTED_ENDER_PEARL',16)],
        'ENCHANTED_FERMENTED_SPIDER_EYE'    : [('ENCHANTED_SPIDER_EYE',64),('SUGAR_CANE',64),('BROWN_MUSHROOM',64)],
        'ENCHANTED_FIREWORK_ROCKET'         : [('ENCHANTED_GUNPOWDER',64),('SUGAR_CANE',16)],
        'ENCHANTED_GLOWSTONE'               : [('ENCHANTED_GLOWSTONE_DUST',192)],
        'ENCHANTED_GOLD'                    : [('GOLD_INGOT',160)],
        'ENCHANTED_GOLD_BLOCK'              : [('ENCHANTED_GOLD',160)],
        'ENCHANTED_GRILLED_PORK'            : [('ENCHANTED_PORK',160)],
        'ENCHANTED_HAY_BLOCK'               : [('HAY_BLOCK',144)],
        'ENCHANTED_IRON'                    : [('IRON_INGOT',160)],
        'ENCHANTED_IRON_BLOCK'              : [('ENCHANTED_IRON',160)],
        'ENCHANTED_LAPIS_LAZULI_BLOCK'      : [('ENCHANTED_LAPIS_LAZULI',160)],
        'ENCHANTED_LAVA_BUCKET'             : [('ENCHANTED_COAL_BLOCK',2),('ENCHANTED_IRON',3)],
        'ENCHANTED_LEATHER'                 : [('LEATHER',576)],
        'ENCHANTED_NETHER_STALK'            : [('NETHER_STALK',160)],
        'ENCHANTED_PACKED_ICE'              : [('ENCHANTED_ICE',160)],
        'ENCHANTED_PAPER'                   : [('SUGAR_CANE',192)],
        'ENCHANTED_POTATO'                  : [('POTATO_ITEM',160)],
        'ENCHANTED_RABBIT_HIDE'             : [('RABBIT_HIDE',576)],
        'ENCHANTED_SUGAR'                   : [('SUGAR_CANE',160)],
        'ENCHANTED_SUGAR_CANE'              : [('ENCHANTED_SUGAR',160)],
        'ENCHANTED_WET_SPONGE'              : [('ENCHANTED_SPONGE',40)],
        'GOLDEN_TOOTH'                      : [('WOLF_TOOTH',128),('ENCHANTED_GOLD',32)],
        'HAY_BLOCK'                         : [('WHEAT',9)],
        'HOT_POTATO_BOOK'                   : [('SUGAR_CANE',3),('ENCHANTED_BAKED_POTATO',1)],
        'REVENANT_VISCERA'                  : [('REVENANT_FLESH',128),('ENCHANTED_STRING',32)],
        'PACKED_ICE'                        : [('ICE',9)],
        'SUPER_COMPACTOR_3000'              : [('ENCHANTED_COBBLESTONE',7*64),('ENCHANTED_REDSTONE_BLOCK',1)],
        'SUPER_EGG'                         : [('ENCHANTED_EGG',144)],
        'TARANTULA_SILK'                     : [('TARANTULA_WEB',128),('ENCHANTED_FLINT',32)],
        
        ##add mushrooms
        ##'ENCHANTED_GLISTERING_MELON'        : (()),
        ##'ENCHANTED_COCOA'
        })

    reforges = ['Demonic','Forceful','Gentle','Godly','Hurtful','Keen','Strong','Superior','Unpleasant','Zealous',
                'Odd','Rich','Epic','Fair','Fast','Heroic','Legendary','Spicy', 'Salty','Treacherous','Deadly',
                'Fine','Grand','Hasty','Neat','Rapid','Unreal','Clean','Fierce','Heavy','Light','Mythic','Pure',
                'Smart','Titanic','Wise',]

    weapon_enchantments = ['Bane of Arthropods','Cleave','Critical','Cubism','Dragon Hunter','Ender Slayer','Execute',
                          'Experience','Fire Aspect','First Strike','Giant Killer','Impaling','Knockback','Lethality',
                          'Life Steal','Looting','Luck','Scavenger','Sharpness','Smite','Telekinesis','Thunderlord',
                          'Vampirism','Venomous','Aiming','Flame','Impaling','Infinite Quiver','Piercing','Punch',
                          'Snipe',]
    armor_enchantments = ['Aqua Affinity','Blast Protection','Depth Strider','Feather Falling','Fire Protection',
                          'Frost Walker','Growth','Projectile Protection','True Protection','Protection','Rejuvenate',
                          'Respiration','Thorns','Sugar Rush',]
    tool_enchantments = ['Efficiency','Experience','Fortune','Harvesting','Rainbow','Replenish','Silk Touch'
                         'Smelting Touch','Telekinesis',]

    tiers = ['COMMON','UNCOMMON','RARE','EPIC','LEGENDARY','SPECIAL']

    print_auction = True


    def __init__(self):
        self.bazaar_data = {
        key : {'data': [], 'delta' : [], 'peak' : {}, 'low' : {},} for key in self.bazaar_items
        }
        with open('bazaar_data.dat','rb') as F:
            self.bazaar_data = pickle.load(F)

        self.ah_data = {}
##        with open('ah_data.dat','rb') as G:
##            self.ah_data = pickle.load(G)

    async def get_bazaar_prices(self):
        context = {
            'key' : self.API_KEY,
            }
        self.last_bazaar_fetch = requests.get(self.web+'skyblock/bazaar',context).json()
        return self.last_bazaar_fetch

    async def get_valuable_upcrafts(self,mode=''):
        bazaar_prices = await self.get_bazaar_prices()
        bazaar_prices = bazaar_prices['products']
        self.bazaar_prices = bazaar_prices
        profits_by_item = {}
        
        for crafted_item in self.up_crafts:
            value = sum(self.get_price(ingredient,amount,bazaar_prices) for ingredient,amount in self.up_crafts[crafted_item])
            number_of_items = sum(amount for ingredient,amount in self.up_crafts[crafted_item])
            profit = bazaar_prices[crafted_item]['sell_summary'][0]['pricePerUnit'] - value
            while profit in profits_by_item:
                profit -= 0.01
            if mode == '':
                profits_by_item[profit] = crafted_item
            elif mode == 'ppi':
                profits_by_item[profit/number_of_items] = (crafted_item,profit)
            elif mode == '%':
                profits_by_item[profit/value] = (crafted_item,profit)
            elif mode == 'upvalue':
                profits_by_item[bazaar_prices[crafted_item]['sell_summary'][0]['pricePerUnit']/value] = (crafted_item,profit)
        profit_margins = list(profits_by_item.keys())
        profit_margins.sort()
        return [(profits_by_item[margin],margin) for margin in profit_margins]

    def get_price(self,ingredient,amount,bazaar_prices):
        prices = bazaar_prices[ingredient]['buy_summary']
        summary_total = 0
        index = 0
        while amount > 0:
            number_available = min(amount,prices[index]['amount'])
            summary_total += number_available*prices[index]['pricePerUnit']
            amount -= number_available
            index += 1
        return summary_total

    async def update_bazaar_data(self):
        self.database_locked = True
        prices = await self.get_bazaar_prices()
        prices = prices['products']
        curr_time = time.time()
        curr_date = datetime.date.today()
        for key in self.bazaar_items:
            try:
                with open('bazaar_data/'+key.upper()+'.dat','rb') as F:
                    past_data = pickle.load(F)
            except FileNotFoundError:
                print(key)
                continue
                past_data = None
            current_price = (prices[key]['quick_status']['buyPrice'],curr_time)
            try:
                if past_data:
                    delta = current_price[0]-past_data[key]['data'][0][0]
            except IndexError:
                delta = 0
                print('FIRST TIME? IF NOT, DEBUG')
            
            if curr_date in past_data[key]['peak']:
                if current_price > past_data[key]['peak'][curr_date]:
                    past_data[key]['peak'][curr_date] = current_price
            else:
                past_data[key]['peak'][curr_date] = current_price
            if curr_date in past_data[key]['low']:
                if current_price < past_data[key]['low'][curr_date]:
                    past_data[key]['low'][curr_date] = current_price
            else:
                past_data[key]['low'][curr_date] = current_price
                
            past_data[key]['data'].insert(0,current_price)
            past_data[key]['delta'].insert(0,(delta,curr_time))
            with open('bazaar_data/'+key.upper()+'.dat','wb') as F:
                pickle.dump(past_data,F)
        #self.backup_bazaar_data()
        self.database_locked = False

##    def backup_bazaar_data(self):
##        curr_time = time.time()
##        curr_data = datetime.date.today()
##        for key in self.bazaar_data.keys():
##            try:
##                with open('bazaar_data/'+key.upper()+'.dat','rb') as F:
##                    data = pickle.load(F)
##            except FileNotFoundError:
##                data = None
##            if data:
##                if curr_date in data[key]['peak']:
##                    if curr_date
##                    t_price
##        #with open('bazaar_data.dat','wb') as F:
##        #    pickle.dump(self.bazaar_data,F)

    async def find_disparities(self):
        if self.database_locked:
            return []
        results = {}
        prices = await self.get_bazaar_prices()['products']
        for key in self.bazaar_items:
            d = round(prices[key]['quick_status']['buyPrice']-prices[key]['quick_status']['sellPrice'],2)
            while d in results:
                d -= 0.01
            results[d] = key
        keys = list(results.keys())
        keys.sort()
        return [str([results[value],value]) for value in keys]

    def find_shakers(self):
        debug = True
        #if self.database_locked:
        #    return []

        #find_image = lambda name: '_'.join([word[0:1].upper()+word[1:].lower() for word in name.split('_')]) + '.webp' if name.upper() in self.bazaar_items else 'Default.png'
        results = []
        messages = []
        for key in self.bazaar_items:
            self.bazaar_data = self.load_bazaar_data(key)
            try:
                avg,var = custom_weighted_stats(self.bazaar_data[key]['data'][1:])
            except Exception as e:
                if key.upper() == 'ENCHANTED_RABBIT_FOOT':
                    continue
                print(str(self.bazaar_data)[0:1000])
                raise e
                
            cdf_result = norm.cdf(avg,var,self.bazaar_data[key]['data'][0][0])
            if not (self.sig_level < cdf_result < 1 - self.sig_level):
                results.append([key,avg])
        if len(results) > 0:
            for name,avg in results:
                self.bazaar_data = self.load_bazaar_data(name)
                data_avg, data_var = custom_weighted_stats(self.bazaar_data[name]['data'][1:])
                try:
                    percent_change = (self.bazaar_data[name]['data'][0][0] - data_avg)/data_avg * 100
                except ZeroDivisionError:
                    continue
                if percent_change > 0:
                    color = 0x00cc66
                else:
                    color = 0xff3300
                embed = discord.Embed(title=' '.join(name.split('_')),color=color,description='Sudden price change!')

                file = discord.File("assets/icons/"+find_image(name),filename='icon.webp')
                embed.set_thumbnail(url='attachment://icon.webp') ##icon.webp defined on the line above
                
                #embed.set_image(url='attachment://assets/icons/'+name+'.png')
                #embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/hypixel-skyblock/images/f/fc/Enchanted_Ice.png/revision/latest?cb=20200215111621.png')
                embed.add_field(name='Date',value=datetime.datetime.now(),inline=False)
                embed.add_field(name='Percent Change',value=round(percent_change,2),inline=False)
                embed.add_field(name='New Price',value=round(self.bazaar_data[name]["data"][0][0],2),inline=False)
                embed.add_field(name='Previous Average',value=round(data_avg,2),inline=False)
                if debug:
                    message = f'{name} has changed by {round(percent_change,2)} percent and has gone to {round(self.bazaar_data[name]["data"][0][0],2)} from the average of {round(data_avg,2)}\n'
                messages.append([embed,file])
        else:
            if hypixel_api.echo:
                print('[]')
        return results,messages

    def load_bazaar_data(self,key):
        while self.database_locked:
            pass
            #return self.load_bazaar_data(key)
        try:
            with open('bazaar_data/'+key.upper()+'.dat','rb') as F:
                return pickle.load(F)
        except FileNotFoundError:
            return -1

    def show_graph(self,key,time_since=3600,option='data'):
        try:
            with open('bazaar_data/'+key.upper()+'.dat','rb') as F:
                self.bazaar_data = pickle.load(F)
        except FileNotFoundError:
            return 0
##        if key not in self.bazaar_items:
##            return 0
        if option not in ['delta','data']:
            return 0
        times = []
        prices = []
        curr_time = time.time()
        for datapoint in self.bazaar_data[key][option]:
            if curr_time - datapoint[1] > time_since:
                continue
            prices.append(datapoint[0])
            times.append(datetime.datetime.fromtimestamp(datapoint[1]))
        plot.plot(times,prices)
        plot.xlabel("Time")
        plot.ylabel(f"Price of {key} (coins)")
        plot.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        #plot.savefig('./graphs/graph.png')
        fig = plot.gcf()
        fig.set_size_inches(10,5)
        fig.savefig('./graphs/graph.png')
        fig = plot.gcf()
        fig.set_size_inches(24,12)
        fig.savefig('./graphs/graph_big.png',dpi=100)
        plot.clf()
        return 1
        #plot.show()

    def clear_graph(self):
        plot.close()

    async def get_ah_data(self,page=0):
        context = {
            'key' : self.API_KEY,
            'page' : page,
            }
        result = requests.get('https://api.hypixel.net/skyblock/auctions',context).json()
        return result

    def assemble_item(self,auction): ##auction is decoded dict
        debug = False

        if self.print_auction:
            print(auction)
            self.print_auction = False
        
        item_bytes = auction['item_bytes']
        item_bytes_decoded = nbt.nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(item_bytes)))
        
        item_name = auction['item_name']
        
        reforge = ''
        if item_name.startswith('Highly Superior Dragon'):
            target = 'Superior Dragon ' + re.sub('Highly Superior Dragon ','',item_name)
            reforge = 'Superior'
        elif item_name.startswith('Very Wise Dragon'):
            target = 'Wise Dragon ' + re.sub('Very Wise Dragon ','',item_name)
            reforge = 'Wise'
        elif item_name.startswith('Very Strong Dragon'):
            target = 'Strong Dragon ' + re.sub('Very Strong Dragon ','',item_name)
            reforge = 'Strong'
        elif item_name.startswith('Extremely Heavy'):
            target = 'Heavy ' + re.sub('Extremely Heavy ','',item_name)
            reforge = 'Heavy'
        elif item_name.startswith('Absolutely Perfect'):
            target = 'Perfect ' + re.sub('Very Strong Dragon ','',item_name)
            reforge = 'Perfect'
        else:
            try:
                reforge = item_bytes_decoded['i'][0]['tag']['ExtraAttributes']['modifier'].value
                reforge = reforge[0:1].upper() + reforge[1:]
            except KeyError:
                reforge = ''
            if reforge != '':
                target = re.sub(reforge + ' ','',item_name)
            else:
                target = item_name
##                        if auction['category'] in ('weapon','armor','tool'):
##                            for reforge_available in self.reforges:
##                                if reforge_available in item_name:
##                                    target = re.sub(reforge_available+' ','',item_name)
##                                    reforge = reforge_available
##                        else:
##                            target = item_name
                
        #target = target.upper()
        metadata = set()
        in_depth_enchantments = {}
        extra = auction['extra']
        try:
            for enchantment in item_bytes_decoded['i'][0]['tag']['ExtraAttributes']['enchantments']:
                metadata.add(enchantment)
                in_depth_enchantments[enchantment] = item_bytes_decoded['i'][0]['tag']['ExtraAttributes']['enchantments'][enchantment].value
        except KeyError:
            pass
        if debug:
            print(auction['extra'])
##                    if auction['category'] in ('armor','tool','weapon'):
##                        if auction['category'] == 'armor':
##                            enchantments = self.armor_enchantments
##                        elif auction['category'] == 'weapon':
##                            enchantments = self.weapon_enchantments
##                        elif auction['category'] == 'tool':
##                            enchantments = self.tool_enchantments
##                        for enchantment in enchantments:
##                            if enchantment in extra:
##                                metadata.add(enchantment)
##                                extra = re.sub(enchantment,'',extra)
##                                
##                    elif item_name == 'Enchanted Book':
##                        for enchantment in set(self.armor_enchantments+self.weapon_enchantments+self.tool_enchantments):
##                            if enchantment in extra:
##                                metadata.add(enchantment)
##                                extra = re.sub(enchantment,'',extra)
                    
        tier = auction['tier']
        category = auction['category']
        selling_price = auction['highest_bid_amount']
        item_count = item_bytes_decoded['i'][0]['Count'].value
        target = re.sub('\u25c6 ','',target)
        target = re.sub("'",'',target)

        adjusted_selling_price = selling_price/item_count

        base_item = ah_item(target,tier,category,'',set(),{})
        secondary_base_item = ah_item(target,tier,category,'',metadata,{})
        result = ah_item(target,tier,category,reforge,metadata,in_depth_enchantments)
        
        return base_item, secondary_base_item, result, adjusted_selling_price

    def find_average_price(self,base_item,tertiary=False):
        if type(base_item) == ah_item:
            item_name = '_'.join(base_item.name.upper().split(' '))
        else:
            raise TypeError
        auctions_data = self.find_auctions(item_name,tertiary)
        if auctions_data:
            average = 0
            count = 0
            if tertiary:
                for item in auctions_data:
                    if item[0] == base_item:
                        average += sum(price for price in item[1])
                        count += len(item[1])
            else:
                for item in auctions_data:
                    for i in range(len(item[1])):
                        for tertiary_item in item[1][i]:
                            average += sum(item[1][i][tertiary_item])
                            count += len(item[1][i][tertiary_item])
##                    average += sum(sum(sum(item[1][i][tertiary_item][tertiary_item.name]) for tertiary_item in item[1][0]) for i in range(len(item[1])))
##                    count += sum(len(item[1][0][tertiary_item][tertiary_item.name])
            return average/count
        else:
            return -1

#e2c30f
    async def snipe_auctions(self):
        debug = False

        embeds = []
        for page_number in range(10):
            auctions = await self.get_ah_data(page=page_number)
            auctions = auctions['auctions']
            curr_time = time.time()
            for auction in auctions:
                try:
                    base_item, secondary_base_item, tertiary_item, adjusted_selling_price = self.assemble_item(auction)
                except TypeError as e:
                    print(auction)
                    print(e)
                    raise e
                if 75 >= auction['end']/1000 - curr_time >= 30:
                    average_price = self.find_average_price(base_item)
                    if base_item.name in ['Stick','Dirt','Arrow']:
                        continue
                    if base_item.tier.lower() in ['common','uncommon']:
                        continue
                    if (auction['highest_bid_amount'] and auction['highest_bid_amount'] <= average_price * 0.8 and average_price > 100000) or (not auction['highest_bid_amount'] and auction['starting_bid'] <= average_price * 0.8 and average_price > 100000):
                        embed = discord.Embed(title=tertiary_item.name,color=0xe2c30f,description='Underpriced item spotted on AH!')
                        
                        file = discord.File('assets/icons/'+find_image(base_item.name),filename=f'icon{len(embeds)}.webp')
                        embed.set_thumbnail(url=f'attachment://icon{len(embeds)}.webp')
                        
                        item_listing_price = auction['highest_bid_amount'] if auction['highest_bid_amount'] else auction['starting_bid']
                        embed.add_field(name='Listed Price',value=item_listing_price)

                        embed.add_field(name='Avg. Selling Price',value=round(average_price,2))

                        seller_name = self.name_from_uuid(auction['auctioneer'])
                        embed.add_field(name='Seller Name:',value=seller_name,inline=False)

                        embeds.append([embed,file])
        return embeds

    def name_from_uuid(self,uuid):
        past_names = requests.get('https://api.mojang.com/user/profiles/'+uuid+'/names').json()
        return past_names[-1]['name']

    async def add_ending_auctions(self):
        debug = False
        
        for page_number in range(10):
            auctions = await self.get_ah_data(page=page_number)
            auctions = auctions['auctions']
            results = []
            curr_time = time.time()
            for auction in auctions:
                if auction['end']/1000 - curr_time <= 15 and auction['highest_bid_amount'] > 0:

                    base_item, secondary_base_item, result, adjusted_selling_price = self.assemble_item(auction)

                    if base_item in self.ah_data:
                        if secondary_base_item in self.ah_data[base_item]:
                            if result in self.ah_data[base_item][secondary_base_item]:
                                self.ah_data[base_item][secondary_base_item][result].insert(0,adjusted_selling_price)
                            else:
                                self.ah_data[base_item][secondary_base_item][result] = [adjusted_selling_price]
                        else:
                            self.ah_data[base_item][secondary_base_item] = {}
                            self.ah_data[base_item][secondary_base_item][result] = [adjusted_selling_price]
                    else:
                        self.ah_data[base_item] = {}
                        self.ah_data[base_item][secondary_base_item] = {}
                        self.ah_data[base_item][secondary_base_item][result] = [adjusted_selling_price]
        self.backup_ah_data()
 
    def backup_ah_data(self):
        for item in self.ah_data.items():
            didIOError = False
            try:
                with open('ah_data/'+item[0].tier.upper()+' '+item[0].name.upper()+'.dat','rb') as F:
                    temp = pickle.load(F)
            except FileNotFoundError:
                temp = {item[0] : self.ah_data[item[0]]}
                didIOError = True
            for key in temp.keys():
                self.key_one = key
            self.key_two = item[0]
            if not didIOError:
                for key in self.ah_data[item[0]]:
                    if key in temp[item[0]]:
                        for tertiary_key in self.ah_data[item[0]][key]:
                            if tertiary_key in temp[item[0]][key]:
                                temp[item[0]][key][tertiary_key] += self.ah_data[item[0]][key][tertiary_key]
                            else:
                                temp[item[0]][key][tertiary_key] = self.ah_data[item[0]][key][tertiary_key]
                    else:
                        temp[item[0]][key] = self.ah_data[item[0]][key]
            with open('ah_data/'+item[0].tier.upper()+' '+item[0].name.upper()+'.dat','wb') as F:
                pickle.dump(temp,F)
        self.ah_data = {}
        
    
    def find_auctions(self,name,verbose=False):
        results = []
        name = name.upper()
        for path in os.listdir('ah_data'):
            if not (path.endswith('.dat')):
                continue
            path_adj = path
            for tier in self.tiers:
                if tier in path_adj:
                    path_adj = re.sub('^'+tier.upper()+' ','',path_adj)
            if path_adj[0:-4] == name: ## 'lol.dat'[0:-4] = 'lol'
                with open('ah_data/'+path,'rb') as F:
                    data = pickle.load(F)
                for key in data.keys(): ##there is only one key
                    for secondary_item in data[key]:
                        if not verbose:
                            results.append([secondary_item, [data[key][secondary_item]]])
                        else:
                            for tertiary_key in data[key][secondary_item]:
                                results.append([tertiary_key, [{tertiary_key : data[key][secondary_item][tertiary_key]}]])
                    #return results
##        for item in self.ah_data:
##            if item.name.upper() == name:
##                for secondary_item in self.ah_data[item]:
##                    results.append([secondary_item, [self.ah_data[item][secondary_item]]])
##                return results
        return results

def custom_weighted_stats(data,all_positive=False): ##data is ordered pair of (value,time)
    change = (lambda data: abs(data)) if all_positive else (lambda data: data)
    data = data[0:90]
    w = weighting_function
    curr_time = time.time()
    start_time = min(pairing[1] for pairing in data)
    ##avg is timeweighted by 2 ** (-x)
    avg = sum((change(pairing[0]) * w(pairing[1],curr_time)) for pairing in data) / sum(w(pairing[1],curr_time) for pairing in data)
    var = sum((w(pairing[1],curr_time) * ((change(pairing[0])-avg) ** 2)) for pairing in data) / (len(data)) / sum(w(pairing[1],curr_time) for pairing in data)
    return avg,var
    
def weighting_function(start_time,curr_time,standard='days'):
    return 10 ** (12*(start_time-curr_time)/86400) / 1440 ## (time - curr_time < 0) is True and 1440 is minutes in day - got to account for em ##also not sure the / 1440 actually does anything?

def integral_correction(old_time,curr_time,standard='days'):
    return 1/(1 - math.e ** ((old_time-curr_time)/86400))
    #return math.log(weighting_base)/(1 - 2 ** ((old_time - curr_time))/86400) ## old_time - curr_time is less than 0 - we are literally evaluating 1 over the integral to standardize to modulus one

async def continually_update(api):
    debug = True
    await api.update_bazaar_data()
    tick = 0
    while True:
        await api.update_bazaar_data()
        #if tick == 0:
            #api.update_bazaar_data()
            #api.find_shakers()
        tick = (1+tick)%3
        await api.add_ending_auctions()
        time.sleep(60)

def gen_func(f,*args,**kwargs):
    return lambda *args2: f(*args,**kwargs)


#------------------------------------#
#------------------------------------#
#------------------------------------#
            # COMMANDS #
#------------------------------------#
#------------------------------------#
#------------------------------------#

bot = commands.Bot(command_prefix='$')

#------------------------------------#
#------------------------------------#
            # BAZAAR #
#------------------------------------#
#------------------------------------#

#------------------------------------#
            # POST HERE #
#------------------------------------#

stop_stonkbot_spam = {key : 0 for key in hypixel_api.bazaar_items}

@bot.command(name='post_here')
@commands.has_role('STONK MASTER')
async def post_here(ctx):
    debug = True
    await ctx.send('Received!')
    while True:
        curr_time = time.time()
        results,messages = api.find_shakers()
        if len(messages) > 0:
            RL = []
            for i in range(len(messages)):
                if curr_time - stop_stonkbot_spam[results[i][0]] < 300:
                    RL.append(i)
                else:
                    stop_stonkbot_spam[results[i][0]] = curr_time
            RL.reverse()
            for i in RL:
                del messages[i]
                del results[i]
            if len(messages) == 0:
                pass
            else:
                for embed in messages:
                    await ctx.send(file=embed[1],embed=embed[0])
                #await ctx.send(str(datetime.datetime.now()) + '\n' + '\n'.join(messages))
        await asyncio.sleep(60)

@bot.command(name='ah_post_here')
@commands.has_role('STONK MASTER')
async def ah_post_here(ctx):
    await ctx.send('AH Received!')
    while True:
        embeds = await api.snipe_auctions()
        for embed,file in embeds:
            await ctx.send(embed=embed,file=file)
        #await ctx.send('Loop complete!')
        await asyncio.sleep(60)
        

#------------------------------------#
            # UPCRAFTS #
#------------------------------------#

@bot.command(name='upcrafts')
@commands.has_role('STONK TRADER')
async def profitable_upcrafts(ctx, mode=''):
    if mode not in ['ppi','%','upvalue','']:
        mode = ''
    uc = await api.get_valuable_upcrafts(mode)
    if mode == '':
        desc = 'These are items you can upcraft for a profit.'
    elif mode == 'ppi':
        desc = 'Sorted by profit per item.'
    elif mode == '%':
        desc = 'Sorted by profit divided by cost.'
    elif mode == 'upvalue':
        desc = 'Sorted by crafted item sell over ingredient buy.'
    embed = discord.Embed(title='Bazaar Upcrafts',color=0xe6e600,description=desc)
    if mode == '':
        for item in uc:
            if item[1] > 0:
                name = item[0].split('_')
                for i in range(len(name)):
                    name[i] = name[i][0:1].upper() + name[i][1:].lower()
                name = ' '.join(name)
                embed.add_field(name='Item Name & Profit', value=name + ' // ' + str(round(item[1],2)),inline=False)
                #embed.add_field(name='Profit', value=round(item[1],2),inline=False)
                #embed.add_field(name='=====',value='=====',inline=False)
    else:
        for item in uc:
            if item[0][1] > 0:
                name = item[0][0].split('_')
                for i in range(len(name)):
                    name[i] = name[i][0:1].upper() + name[i][1:].lower()
                name = ' '.join(name)
                embed.add_field(name='Item Name & Profit', value=name + ' // ' + str(round(item[0][1],2)),inline=False)
                #embed.add_field(name='Profit', value=round(item[0][1],2))
                if mode == 'ppi':
                    embed.add_field(name='Profit per Item',value=round(item[1],2))
                elif mode == '%':
                    embed.add_field(name='Profit divided by Cost',value=round(item[1],2))
                elif mode == 'upvalue':
                    embed.add_field(name='Item Sell divided by Ingredient Buy',value=round(item[1],2))
                #embed.add_field(name='=====',value='=====',inline=False)
    await ctx.send(embed=embed)

##        profitable_uc = [str(item) for item in uc if item[1] > 0]
##    elif mode == 'ppi':
##        profitable_uc = [str([item[0][0],round(item[0][1],2)]) + f'\n Profit per item: {round(item[1],2)}\n' for item in uc if item[0][1] > 0]
##        profitable_uc.append('SORTED BY PROFIT PER ITEM')
##    elif mode == '%':
##        profitable_uc = [str([item[0][0],round(item[0][1],2)]) + f'\n Profit divided by cost: {round(item[1],2)}\n' for item in uc if item[0][1] > 0]
##        profitable_uc.append('SORTED BY PROFIT DIVIDED BY COST')
##    elif mode == 'upvalue':
##        profitable_uc = [str([item[0][0],round(item[0][1],2)]) + f'\n Crafted item sell over ingredient buy: {round(item[1],2)}\n' for item in uc if item[0][1] > 0]
##    await ctx.send('\n'.join(profitable_uc))

#------------------------------------#
            # DISPARITY #
#------------------------------------#

@bot.command(name='disparity')
@commands.has_role('STONK TRADER')
async def disparity(ctx):
    dis = await api.find_disparities()
    message = '\n'.join(dis)
    with open('disparities.txt','w+') as F:
        F.write(message)
    await ctx.send(file=discord.File('disparities.txt'))
##    while len(message) > 2000:
##        message, m = message[2000:], message[0:2000]
##        await ctx.send(m)
##    await ctx.send(message)

#------------------------------------#
            # SENDGRAPH #
#------------------------------------#

@bot.command(name='sendgraph')
@commands.has_role('STONK TRADER')
async def send_graph(ctx,key,*args):
    big_graph = False
    time_since = 3600
    for arg in args:
        if arg in ('-b'):
            if arg == '-b':
                big_graph = True
        try:
            time_since = int(arg)
        except ValueError:
            pass
    key = key.upper()
    if key in item_map.bazaar_items:
        key = item_map.bazaar_items[key]
    try:
        int(time_since)
    except:
        await ctx.send('Invalid arguments.')
        return
    if api.show_graph(key,int(time_since)):
        if big_graph:
            with open('graphs/graph_big.png','rb') as F:
                await ctx.send(file=discord.File(F))
        else:
            with open('graphs/graph.png','rb') as F:
                await ctx.send(file=discord.File(F))
    else:
        await ctx.send('Key not found!')

#------------------------------------#
#------------------------------------#
            # AUCTIONS #
#------------------------------------#
#------------------------------------#

#------------------------------------#
           # FIND VALUE #
#------------------------------------#
    

@bot.command(name='value')
@commands.has_role('STONK TRADER')
async def find_value(ctx,*args):
    debug = False
    verbose = False
    endless = False
    filters_found = True
    is_pet = False

    while filters_found:
        filters_found = False
        if args[0] == '-v':
            filters_found = True
            verbose = True
            args = list(args)[1:]
        if args[0] == '-a':
            filters_found = True
            endless = True
            args = list(args)[1:]
        if args[0] == '-h':
            filters_found = True
            await has_enchant(ctx,args[1],' '.join(args[2:]),endless)
            return

    if args[-1].lower() == 'pet':
        is_pet = True
        args = list(args[0:-1])
    name = ' '.join(args)
##    if '[lvl' in name.lower():
##        name = re.sub(r'\[lvl [0-9]+\] ','',name.lower())
##        is_pet = True
    bazaar_adj_name = '_'.join(args).upper()
    old_name = ''
    if name.lower() == 'xanos':
        embed = discord.Embed(title='Pricing',color=0xe6e600)
        embed.add_field(name='Buy Price',value='Priceless')
        embed.add_field(name='Sell Price',value='Priceless')
        file = discord.File('assets/icons/profilephoto.png',filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        await ctx.send(file=file,embed=embed)
        return
    if bazaar_adj_name in item_map.bazaar_items:
        old_name = bazaar_adj_name
        bazaar_adj_name = item_map.bazaar_items[bazaar_adj_name]
    if bazaar_adj_name in hypixel_api.bazaar_items:
        #find_image = lambda name: '_'.join([word[0:1].upper()+word[1:].lower() for word in name.split('_')]) + '.webp' if '_'.join([word[0:1].upper()+word[1:].lower() for word in name.split('_')])+'.webp' in os.listdir('assets/icons') else 'Default.png'

        prices = api.last_bazaar_fetch['products'][bazaar_adj_name]['quick_status']
        buyPrice = round(prices['buyPrice'],2)
        sellPrice = round(prices['sellPrice'],2)

        embed = discord.Embed(title='Bazaar Pricing',color=0xe6e600)

        if old_name:
            file = discord.File('assets/icons/'+find_image(old_name),filename='icon.webp')
        else:
            file = discord.File('assets/icons/'+find_image(bazaar_adj_name),filename='icon.webp')
        embed.set_thumbnail(url='attachment://icon.webp')
        
        embed.add_field(name='Buy Price',value=buyPrice)
        embed.add_field(name='Sell Price',value=sellPrice)
        await ctx.send(file=file,embed=embed)
        #await ctx.send(f'BAZAAR PRICING:\nBuy Price: {buyPrice}\nSellPrice: {sellPrice}')
        return

    if is_pet:
        results = []
        for level in range(1,101):
            results += api.find_auctions(f'[Lvl {level}] ' + name,verbose=verbose)
    else:
        results = api.find_auctions(name,verbose=verbose)
    
    if results == []:
        embed = discord.Embed(title='No results found!',color=0xe6e600,description=f'Unfortunately, no results were found in the auction house for {name}.')
        await ctx.send(embed=embed)
        return
    messages = []
    for r in results:
        prices = []
        #item_name = r[0].name
        ##r[0].enchantments will always be {} because r[0].enchantments is only for tracking enchantment levels
        #m = f'Enchantments: {", ".join([ench[0:1].upper() + ench[1:] for ench in r[0].metadata])}\nAvg. Selling Price: '
        m = {
            'Name'          : str(r[0]),
            'Category'      : r[0].category[0:1].upper() + r[0].category[1:].lower(),
            'Tier'          : r[0].tier[0:1].upper() + r[0].tier[1:].lower(),
            'Enchantments'  : ", ".join([ench[0:1].upper() + ench[1:] for ench in r[0].metadata]),
             }
        if verbose:
            m['Enchantments'] = ", ".join([ench[0:1].upper() + ench[1:] + ' ' + str(r[0].enchantments[ench]) for ench in r[0].enchantments])
        for item in r[1]:
            for key in item.keys():
                prices += item[key]
        #m += f'{round(sum(prices)/len(prices),2)}\nNum. Recorded Listings: {len(prices)}\n'
        m.update({
            'Avg. Selling Price: '  : round(sum(prices)/len(prices),2),
            'Recorded Listings: '   : len(prices),
            })
        messages.append([m,len(prices)])
    amounts = {}
    i = 0
    for m in messages:
        while m[1] in amounts:
            m[1] -= 0.1
        amounts[m[1]] = i
        i += 1
    temp_keys = list(amounts.keys())
    temp_keys.sort()
    temp_keys.reverse()
    adj_messages = []
    if len(temp_keys) <= 3 or endless:
        for key in temp_keys:
            adj_messages.append(messages[amounts[key]][0])
    else:
        for key in temp_keys[0:3]:
            adj_messages.append(messages[amounts[key]][0])
    #embed = discord.Embed(title='AH: ' + name.upper(), color=0xe6e600,description='Auction House Pricings')

    if is_pet:
        name = name + ' Pet'
    for mes in adj_messages:
        embed = discord.Embed(title=mes['Name'],color=0xe6e600,description=mes['Tier'] + ' ' + mes['Category'])

        file = discord.File('assets/icons/'+find_image(name),filename='icon.webp')
        embed.set_thumbnail(url='attachment://icon.webp')
        
        for item in mes.items():
            if item[0] in ('Category','Tier','Name'):
                continue
            temp_item1 = item[1]
            if temp_item1 == '' or temp_item1 == None:
                temp_item1 = 'None'
            embed.add_field(name = item[0], value = temp_item1, inline = False)
        await ctx.send(file=file,embed=embed)
    #res = '\n'.join(adj_messages)
    #while len(res) > 2000:
    #    first_res, res = res[0:2000], res[2000:]
    #    await ctx.send(first_res)
    #if len(results) == 0:
    #    await ctx.send('Unfortunately the requested item could not be found. Please check to ensure that you spelt its name correctly. StonkBot may also not have registered all items yet so please be patient.')
    #    return
    #await ctx.send(res)
    #await ctx.send(embed=embed)

#------------------------------------#
          # TRACKED ITEMS #
#------------------------------------#

@bot.command(name='trackeditems')
@commands.has_role('STONK TRADER')
async def tracked_items(ctx):
    names = []
    for key in os.listdir('ah_data/'):
        names.append(key[0:-4])
    names.sort()
    names = '\n'.join(names)
    with open('names.txt','w+') as F:
        F.write(names)
    await ctx.send(file=discord.File('names.txt'))
    #with open('names.txt','r') as F:
        #print('sending!')
        #await ctx.send(file=discord.File(F))

#------------------------------------#
            # ENCHBOOK #
#------------------------------------#

#alias for $hasenchant <ench> Enchanted Book

@bot.command(name='enchbook')
@commands.has_role('STONK TRADER')
async def enchbook(ctx,*args):
    endless = False
    if args[0] == '-a':
        endless = True
        args = list(args)[1:]
    await has_enchant(ctx,' '.join(args),'Enchanted Book',endless)

#------------------------------------#
            # HAS ENCHANT #
#------------------------------------#

#@bot.command(name='enchbook')
#@commands.has_role('STONK TRADER')
async def has_enchant(ctx,ench,name,endless=False):
    if len(name) == 0 or len(ench) == 0:
        await ctx.send('Invalid syntax. No arguments supplied.')
        return
    ench = ench.split(' ')
    if len(ench)%2 != 0:
        await ctx.send('Arguments must in the form <Enchantment> <Modifier>')
    results = []
    for i in range(int(len(ench)/2)):
        try:
            int(ench[2*i+1])
        except ValueError:
            await ctx.send('You must provide enchantment levels as integers. Did you do it as roman numerals by mistake?')
            return
        results.append([ench[2*i].lower(),int(ench[2*i+1])])
    #name = ' '.join(list(args))
    ebooks = api.find_auctions(name)
    output = []
    for ebook in ebooks:
        if all(enchantment[0] in ebook[0].metadata for enchantment in results):
            for tertiary_ebook in ebook[1]:
                for key in tertiary_ebook:
                    if all(key.enchantments[enchantment[0]] == enchantment[1] for enchantment in results):
                        output.append([key,tertiary_ebook[key]])
    messages = []
    for result in output:
        ench_message = ', '.join([item[0][0:1].upper() + item[0][1:] + ' ' + str(item[1]) for item in result[0].enchantments.items()])
        avg_selling_price = round(sum(result[1])/len(result[1]),2)
        m = {
            'Name'                  : str(result[0]),
            'Category'              : result[0].category[0:1].upper() + result[0].category[1:].lower(),
            'Tier'                  : result[0].tier[0:1].upper() + result[0].tier[1:].lower(),
            'Enchantments'          : ench_message,
            'Avg. Selling Price'    : avg_selling_price,
            'Num. Recorded Listings': len(result[1]),
            
            }
        #m = f"Name: Enchanted Book\nEnchantments: {ench_message}\nAvg. Selling Price: {avg_selling_price}\nNum. Recorded Listings: {len(result[1])}\n"
        messages.append(m)
    #res = '\n'.join(messages)
    count = 0
    for data in messages:
        #adj_name = ' '.join([n[0:1].upper() + n[1:].lower() for n in 
        embed = discord.Embed(title=data['Name'],color=0xe6e600,description=data['Tier'] + ' ' + data['Category'])
        
        file = discord.File('assets/icons/'+find_image(name),filename='icon.webp')
        embed.set_thumbnail(url='attachment://icon.webp')
        
        for field in data:
            if field in ('Category','Name','Tier'):
                continue
            embed.add_field(name=field,value=data[field],inline=False)
        await ctx.send(file = file, embed = embed)
        if count >= 3 and not endless:
            break
        count += 1
    if len(messages) == 0:
        await ctx.send('No items found!')
##    if len(res) == 0:
##        await ctx.send('No books found!')
##    while len(res) > 2000:
##        to_send, res = res[0:2000], res[2000:]
##        await ctx.send(to_send)
##    if len(res) > 0:
##        await ctx.send(res)

#------------------------------------#
#------------------------------------#
              # ADMIN #
#------------------------------------#
#------------------------------------#
    

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command('testembed')
@commands.has_role('STONK MASTER')
async def testembed(ctx):
    embed = discord.Embed(title='Test embed!',color=3447003,description='A very simple Embed!')
    await ctx.send(embed=[embed,embed])



##@bot.event
##async def on_command_error(ctx,error):
##    if isinstance(error,discord.ext.commands.errors.MissingRole):
##        return
##    else:
##        print(error)

api = hypixel_api()
T = threading.Thread(target=gen_func(asyncio.run,continually_update(api)))
T.start()
#loop = asyncio.get_event_loop()
#loop.run_until_complete(continually_update())
##def start():
##    continually_update(api)
##T = threading.Thread(target=gen_func(continually_update,api))
##T.start()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
