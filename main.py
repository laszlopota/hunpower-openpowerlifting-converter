from src.script.Competition import Competition


competition = Competition("2ndDivisionNationals2022")
competition.save_url()
competition.save_original_csvs()
competition.save_meet_csv(True)
competition.save_entries_csv(True)
