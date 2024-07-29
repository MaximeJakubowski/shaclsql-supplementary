import random

def decision(probability):
    return random.random() < probability

def generate(filename, humans, prob_dupl_mail):
    with open(filename, 'w') as f:
        for human_id in range(1, humans + 1):
            if human_id % 100 == 0:
                print(human_id, "/", humans)
            human_iri = f'<human{human_id}>'

            email_pred_iri = f'<http://example.com/email>'

            mail_id = human_id
            if decision(prob_dupl_mail):
                mail_id = human_id - 1

            mail_literal = f'"mail{mail_id}"'

        
            f.write(f"{human_iri} {email_pred_iri} {mail_literal} .\n")

if __name__ == '__main__':
    mio = 10
    generate(f"synthetic_data/ds_data7/data7_{mio}mio.ttl", 1000000*mio, 0.1)
