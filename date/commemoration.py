import datetime

def get_together_days_msg() -> str:
    start_date = datetime.datetime(2017, 4, 2)
    current_date = datetime.datetime.now()
    together_days = current_date - start_date
    return f'距离2017年4月2日，我们已经在一起 {together_days.days} 天！\n\n'