from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from apify_client import ApifyClient
from datetime import datetime
import matplotlib.pyplot as plt
app = Flask(__name__, static_url_path='/static', static_folder='static')

instagram_client = ApifyClient("apify_api_N4DZvGN8WZEdODwNWsJa98aowAZ1030tPMLt")
facebook_client = ApifyClient("apify_api_TREn6wGABw3ijaggDChucNKYPdwEvA3R4YLQ")
twitter_client = ApifyClient("apify_api_ynmJu16VrYLymosVbrV5CAVxK23CKH0uVVea")

@app.route('/')
def index():
    return render_template('firstpage.html')

@app.route('/get_started', methods=['GET', 'POST'])
def get_started():
    if request.method == 'POST':
        # Process the input from getstarted.html
        platform = request.form.get('platform')
        content_type = request.form.get('content_type')

        # Your processing logic here

        # After processing, you can redirect back to firstpage.html or any other page
        return redirect(url_for('index'))

    return render_template('getstarted.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    platform = request.form.get('platform')
    content_type = request.form.get('content_type')

    if platform == 'instagram':
        if content_type == 'comments':
            instagram_url = request.form.get('post_link')
            run_input = {
                "directUrls": [instagram_url],
                "resultsLimit": 24,
            }
            run = instagram_client.actor("apify/instagram-comment-scraper").call(run_input=run_input)
            results_list = []
            for item in instagram_client.dataset(run["defaultDatasetId"]).iterate_items():
                results_list.append(item)
            data = pd.DataFrame(results_list)
            return render_template('instagram_comments.html', data=data)

        elif content_type == 'posts':
            instagram_url = request.form.get('post_link')
            run_input = {
                "username": [instagram_url],
                "resultsLimit": 30,
            }
            run = instagram_client.actor("apify/instagram-post-scraper").call(run_input=run_input)
            result_list2 = []
            for item in instagram_client.dataset(run["defaultDatasetId"]).iterate_items():
                result_list2.append(item)
            data = pd.DataFrame(result_list2)
            return render_template('instagram_posts.html', data=data)
        
        elif content_type == 'profile':
            instagram_url = request.form.get('username')
            run_input = {
                "username": [instagram_url],
                "resultsLimit": 30,
            }
            run = instagram_client.actor("apify/instagram-post-scraper").call(run_input=run_input)
            result_list_profile = []
            for item in instagram_client.dataset(run["defaultDatasetId"]).iterate_items():
                result_list_profile.append(item)
            data = pd.DataFrame(result_list_profile)

            run_input = {"usernames": [instagram_url]}
            run = instagram_client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
            result_list3 = []
            for item in instagram_client.dataset(run["defaultDatasetId"]).iterate_items():
                result_list3.append(item)
            data1 = pd.DataFrame(result_list3)
            columns_to_pass = ['profilePicUrl', 'url', 'biography', 'followersCount', 'followsCount', 'verified', 'username','postsCount']
            profile_data = data1[columns_to_pass].iloc[0].to_dict()


            average_likes = int(data['likesCount'].mean())
            average_comments = int(data['commentsCount'].mean())
            data['likesCount'] = data['likesCount'].astype(int)  # Convert likesCount to integer
            last_10_posts = data.head(10)
            x_likes = range(1, 11)  # Post number
            y_likes = last_10_posts['likesCount'].tolist()

            # Calculate Comments per Post (last 10 posts)
            data['commentsCount'] = data['commentsCount'].astype(int)  # Convert commentsCount to integer
            x_comments = range(1, 11)  # Post number
            y_comments = last_10_posts['commentsCount'].tolist()
            # Calculate Engagement Rate
            total_likes = data['likesCount'].sum()
            total_comments = data['commentsCount'].sum()
            total_posts = len(data)
            engagement_rate = (total_likes + total_comments) / total_posts
            data['timestamp'] = data['timestamp'].apply(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y %H:%M:%S"))
            data = data.sort_values(by='timestamp', ascending=False)
            return render_template(
                'instagram_profile.html', 
                data=data,
                profile_data=profile_data, 
                average_likes=average_likes, 
                average_comments=average_comments,
                x_likes=x_likes,
                y_likes=y_likes,
                x_comments=x_comments,
                y_comments=y_comments,
                engagement_rate=engagement_rate,
                likes_data = y_likes,
                comments_data = y_comments
            )
        
        elif content_type == 'overview':
            instagram_profile = request.form.get('overview')
            run_input = {"usernames": [instagram_profile]}
            run = instagram_client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
            result_list3 = []
            for item in instagram_client.dataset(run["defaultDatasetId"]).iterate_items():
                result_list3.append(item)
            data = pd.DataFrame(result_list3)
            return render_template('instagram_overview.html', data=data)

    elif platform == 'facebook':
        if content_type == 'pages':
            facebook_page_url = request.form.get('post_link')  # Make sure to change the input name
            run_input = {"startUrls": [{"url": facebook_page_url}]}
            run = facebook_client.actor("apify/facebook-pages-scraper").call(run_input=run_input)
            result_list5 = []
            for item in facebook_client.dataset(run["defaultDatasetId"]).iterate_items():
                result_list5.append(item)
            data = pd.DataFrame(result_list5)
            return render_template('facebook_pages.html', data=data)

    elif platform == 'twitter':
        if content_type == 'profiles':
            twitter_profile = request.form.get('profile_name')
            run_input = {
                "handles": [twitter_profile],
                "tweetsDesired": 100,
                "addUserInfo": True,
                "startUrls": [],
                "proxyConfig": {"useApifyProxy": True},
            }
            run = twitter_client.actor("quacker/twitter-scraper").call(run_input=run_input)
            result_list6 = []
            for item in twitter_client.dataset(run["defaultDatasetId"]).iterate_items():
                extracted_data = {
                    "full_text": item["full_text"],
                    "reply_count": item["reply_count"],
                    "retweet_count": item["retweet_count"],
                    "favorite_count": item["favorite_count"],
                    "url": item["url"],
                    "created_at": item["created_at"],
                }
                result_list6.append(extracted_data)
            data = pd.DataFrame(result_list6)
            return render_template('twitter_profiles.html', data=data)

    return "No data scraped."

def format_timestamp(timestamp):
   
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Format the datetime object as desired (DD/MM/YYYY HR:MIN:SEC)
    formatted_timestamp = dt.strftime("%d/%m/%Y %H:%M:%S")
    
    return formatted_timestamp

# Register the custom filter with Flask
app.jinja_env.filters['format_timestamp'] = format_timestamp

if __name__ == '__main__':
    app.run(debug=True)
