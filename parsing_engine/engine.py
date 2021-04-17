#! /usr/bin/env python3

import re


def open_user_page(driver,account,page_info):
    if page_info=="main":
        page_info=""
    driver.get('https://twitter.com/' + account+"/"+page_info)


def open_search_page(driver,from_account,to_account,start_date_str,end_date_str,hashtag=None,words=None,lang=None):
    from_account = "(from%3A" + from_account + ")%20" if from_account is not None else ""
    to_account = "(to%3A" + to_account + ")%20" if to_account is not None else ""
    hash_tags = "(%23" + hashtag + ")%20" if hashtag is not None else ""

    if words is not None:
        # words = str(words).split("//")
        words = "(" + str('%20OR%20'.join(words)) + ")%20"
    else:
        words = ""

    if lang is not None:
        lang = 'lang%3A' + lang
    else:
        lang = ""

    end_date = "until%3A" + end_date_str + "%20"
    start_date = "since%3A" + start_date_str + "%20"

    # print('https://twitter.com/search?q=' + words + from_account + to_account + hash_tags + end_date + start_date + lang + '&src=typed_query' + display_type)
    driver.get('https://twitter.com/search?q=' + words + from_account + to_account + hash_tags + end_date + start_date + lang + '&src=typed_query&f=live')


def get_single_tweet(card):
    # Extract data from tweet card

    try:
        promoted = card.find_element_by_xpath('.//div[2]/div[2]/[last()]//span').text == "Promoted"
    except:
        promoted = False
    finally:
        if promoted:
            return
    
    try:
        userID = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except:
        return

    try:
        postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except:
        return

    try:
        comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except:
        comment = ""

    try:
        responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except:
        responding = ""

    text = comment + responding

    return (userID, postdate, text)

def get_page_tweets(driver,account,data,writer,tweet_ids,logger):

    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    for card in page_cards:
        tweet = get_single_tweet(card)
        if tweet and tweet[0]=='@'+account:
            # check if tweet sent by the designated account
            # ince checked, userID not longer needed
            tweet = tweet[1:] 
            # check if the tweet is unique
            # We assume each user publish at most one tweet at a time.
            tweet_id = tweet[0] # Timestamp
            if tweet_id not in tweet_ids:
                tweet_ids.add(tweet_id)
                data.append(tweet)
                writer.writerow(tweet)
                logger.info("Found tweet at "+str(tweet[0]))

    return driver, data, writer, tweet_ids
