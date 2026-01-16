"""
对战等级分计算器
实现根据对战结果计算等级分和经验值的变化
"""
from django.utils import timezone


class RatingCalculator:
    """等级分计算器"""
    
    # 奖励时间（秒）- 根据题目难度递增
    # 难度 0（入门）: 3分钟
    # 难度 1（普及-）: 10分钟
    # 难度 2（普及/提高-）: 15分钟
    # 难度 3（普及+/提高）: 20分钟
    # 难度 4（提高+/省选-）: 25分钟
    # 难度 5（省选/NOI-）: 30分钟
    # 难度 6（NOI/NOI+/CTSC）: 35分钟
    # 难度 7+: 40分钟
    BONUS_TIME_BY_DIFFICULTY = {
        0: 180,   # 3分钟
        1: 600,   # 10分钟
        2: 900,   # 15分钟
        3: 1200,  # 20分钟
        4: 1500,  # 25分钟
        5: 1800,  # 30分钟
        6: 2100,  # 35分钟
        7: 2400,  # 40分钟
    }
    
    @staticmethod
    def get_bonus_time(difficulty):
        """根据题目难度获取奖励时间（秒）"""
        if difficulty is None:
            difficulty = 1  # 默认普及难度
        # 确保难度在有效范围内
        difficulty = max(0, min(7, difficulty))
        return RatingCalculator.BONUS_TIME_BY_DIFFICULTY.get(difficulty, 600)
    
    @staticmethod
    def calculate_rating_change(user_a_data, user_b_data, room_start_time, difficulty=None):
        """
        计算双方的等级分和经验变化
        
        Args:
            user_a_data: A方数据 {'ac_time': datetime/None, 'gave_up': bool}
            user_b_data: B方数据 {'ac_time': datetime/None, 'gave_up': bool}
            room_start_time: 对战开始时间
            
        Returns:
            {
                'user_a': {'rating_change': int, 'exp_change': int, 'is_win': bool, 'bonus_time': bool},
                'user_b': {'rating_change': int, 'exp_change': int, 'is_win': bool, 'bonus_time': bool}
            }
        """
        a_ac_time = user_a_data.get('ac_time')
        a_gave_up = user_a_data.get('gave_up', False)
        b_ac_time = user_b_data.get('ac_time')
        b_gave_up = user_b_data.get('gave_up', False)
        
        # 根据题目难度获取奖励时间
        bonus_time_seconds = RatingCalculator.get_bonus_time(difficulty)
        
        # 检查是否在奖励时间内完成
        a_bonus = False
        b_bonus = False
        if a_ac_time and room_start_time:
            time_diff = (a_ac_time - room_start_time).total_seconds()
            a_bonus = time_diff <= bonus_time_seconds
        if b_ac_time and room_start_time:
            time_diff = (b_ac_time - room_start_time).total_seconds()
            b_bonus = time_diff <= bonus_time_seconds
        
        # 特判规则：双方都超时且均未AC/放弃
        if not a_ac_time and not a_gave_up and not b_ac_time and not b_gave_up:
            return {
                'user_a': {'rating_change': -20, 'exp_change': 0, 'is_win': False, 'bonus_time': False},
                'user_b': {'rating_change': -20, 'exp_change': 0, 'is_win': False, 'bonus_time': False}
            }
        
        # 规则1：首先AC
        if a_ac_time and (not b_ac_time or a_ac_time < b_ac_time):
            bonus = 5 if a_bonus else 0
            return {
                'user_a': {'rating_change': 15 + bonus, 'exp_change': 10, 'is_win': True, 'bonus_time': a_bonus},
                'user_b': {'rating_change': -12 if b_gave_up else -2 + (5 if b_bonus else 0), 
                          'exp_change': 0 if b_gave_up else 5, 'is_win': False, 'bonus_time': b_bonus}
            }
        
        # 规则1（B方首先AC）
        if b_ac_time and (not a_ac_time or b_ac_time < a_ac_time):
            bonus = 5 if b_bonus else 0
            return {
                'user_a': {'rating_change': -12 if a_gave_up else -2 + (5 if a_bonus else 0), 
                          'exp_change': 0 if a_gave_up else 5, 'is_win': False, 'bonus_time': a_bonus},
                'user_b': {'rating_change': 15 + bonus, 'exp_change': 10, 'is_win': True, 'bonus_time': b_bonus}
            }
        
        # 规则4：对方AC/放弃之前，先放弃
        if a_gave_up and not b_gave_up and not b_ac_time:
            return {
                'user_a': {'rating_change': -15, 'exp_change': 0, 'is_win': False, 'bonus_time': False},
                'user_b': {'rating_change': 15, 'exp_change': 10, 'is_win': True, 'bonus_time': False}
            }
        
        if b_gave_up and not a_gave_up and not a_ac_time:
            return {
                'user_a': {'rating_change': 15, 'exp_change': 10, 'is_win': True, 'bonus_time': False},
                'user_b': {'rating_change': -15, 'exp_change': 0, 'is_win': False, 'bonus_time': False}
            }
        
        # 规则5：对方放弃后，你放弃
        if a_gave_up and b_gave_up:
            # 谁先放弃谁输
            if user_a_data.get('gave_up_time') and user_b_data.get('gave_up_time'):
                if user_a_data['gave_up_time'] < user_b_data['gave_up_time']:
                    return {
                        'user_a': {'rating_change': -15, 'exp_change': 0, 'is_win': False, 'bonus_time': False},
                        'user_b': {'rating_change': 2, 'exp_change': 0, 'is_win': True, 'bonus_time': False}
                    }
                else:
                    return {
                        'user_a': {'rating_change': 2, 'exp_change': 0, 'is_win': True, 'bonus_time': False},
                        'user_b': {'rating_change': -15, 'exp_change': 0, 'is_win': False, 'bonus_time': False}
                    }
        
        # 默认平局
        return {
            'user_a': {'rating_change': 0, 'exp_change': 0, 'is_win': False, 'bonus_time': False},
            'user_b': {'rating_change': 0, 'exp_change': 0, 'is_win': False, 'bonus_time': False}
        }
    
    @staticmethod
    def get_or_create_rating(user, season=None):
        """获取或创建用户的等级分记录"""
        from .models import BattleRating
        
        rating, created = BattleRating.objects.get_or_create(
            user=user,
            season=season,
            defaults={
                'rating': 500,
                'battle_level': 1,
                'experience': 0,
            }
        )
        return rating
