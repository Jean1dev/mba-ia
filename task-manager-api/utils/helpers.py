# LOW: funções utilitárias sem tipagem
def validate_priority(p):
    # LOW: magic numbers sem constante nomeada
    return 1 <= p <= 5

def format_date(d):
    if not d:
        return None
    return str(d)

# LOW: função não utilizada em nenhum lugar
def calculate_progress(done, total):
    if total == 0:
        return 0
    return round((done / total) * 100, 2)
