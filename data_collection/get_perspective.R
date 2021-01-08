library(peRspective)
library(usethis)
library(dplyr)
library(cgwtools)
library(stringr)

options(scipen = 999)

getToxicity = function(text, idx, this.script = 1,
                       api.choice = 'not set',
                       sleepz = 30,
                       file_name = paste("perspective/perspective_tweets_",api.choice,".csv",sep = "")){
  dat.this.time = Sys.Date()

  if(api.choice == 'not set'){
    api.choice = this.script
  }

  api.key.all = c("xxxxxxxxxxxxxxxxxx",
                  "yyyyyyyyyyyyyyyyyy"
                  )

  api_key = api.key.all[[api.choice]]

  print(paste0('dat.this.time is: ', dat.this.time,
               ' and the API is: ', api_key,
               ' and this.script is equal to: ', this.script))

  result_sentence = data.frame(matrix(ncol = 17, nrow = 0))

  for (i in 1:length(text)){
    print(i)

    if(i %% 100 == 0){
      print(Sys.time())
      print(text_scores)
      print(paste0('sleeping for ', sleepz, ' seconds'));
      Sys.sleep(sleepz);
    }

    # Collect scores
    text_scores <- prsp_score(
      text = text[[i]],
      #score_sentences = T,
      languages = "en", 
      score_model = peRspective::prsp_models, 
      key = api_key
    )
    #Sys.sleep(1)
    text_scores$id = idx[[i]]
    #text_scores$text = text[[i]]
    
    write.table(text_scores, file_name,
                sep = ",", col.names = !file.exists(file_name), row.names = F, append = T)
  }

  save(result_sentence,
       file = paste0("temp_toxicity_", this.script, ".RData"))

  return(result_sentence)
}

args = commandArgs(trailingOnly=TRUE)
api.choice = as.numeric(args[2])
week_to_process = as.numeric(args[1])
print(paste("args", api.choice, "week to process", week_to_process))

tweets <- readr::read_csv(paste("data/raw/seed_tweets_20",week_to_process,".csv", sep=""))
tweets <- tweets[!is.na(tweets$text), ] %>% unique()

tweets$text <- str_replace_all(tweets$text, "@\\S+", "@username")
tweets$text <- str_replace_all(tweets$text, "http\\S+", "url")

file_name <- paste("perspective/perspective_tweets_",week_to_process,".csv",sep = "")

getToxicity(text = tweets$text, idx = tweets$id, api.choice = api.choice,
            file_name = file_name)

perspective <- readr::read_csv(file_name)

all_tweets <- merge(tweets, perspective[c('id','TOXICITY')],how='left')

write.table(all_tweets, 'perspective/all_seed_tweets_with_scores.csv',
            sep = ",", col.names = !file.exists(file_name), row.names = F, append = T)