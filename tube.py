from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st

#API key connection
def api_connect():
    api_id="AIzaSyBlPsV_LVeN5KuebN12oE7KqE6pQPIifzM"
    api_service_name="youtube"
    api_version="v3"
    yt=build(api_service_name,api_version,developerKey=api_id)
    return yt
yt=api_connect()

#get Channel information
def get_channel_info(channel_id):
    request=yt.channels().list(
        part="snippet,ContentDetails,statistics", id=channel_id
    )
    response=request.execute()
    for i in response['items']:
        data=dict(Channel_Name=i['snippet']['title'],
                Channel_Id=i['id'],
                Subscribers=i['statistics']['subscriberCount'],
                Views=i['statistics']['viewCount'],
                Total_Videos=i['statistics']['videoCount'],
                Channel_Description=i['snippet']['description'],
                Playlist_Id=i['contentDetails']['relatedPlaylists']['uploads'])
    return data

#Get Video ids
#Using Playlist_Id we can retrieve the video id
def get_videos_ids(channel_id):
    video_ids=[]
    res=yt.channels().list(id=channel_id,
                        part='contentDetails').execute()
    Playlist_id=res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token=None
    while True:
        res1=yt.playlistItems().list(
                                part='snippet',
                                playlistId=Playlist_id,
                                maxResults=50,
                                pageToken=next_page_token).execute()
        for i in range(len(res1['items'])):
            video_ids.append(res1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token=res1.get('nextPageToken')   
        if next_page_token is None:
            break
    return video_ids


#Video details
def get_video_info(video_ids):
    video_data=[]
    for vid_id in video_ids:
        request=yt.videos().list(
            part="snippet,ContentDetails,statistics",
            id=vid_id
        )
        response=request.execute()
        for item in response["items"]:
            data=dict(Channel_Name=item["snippet"]["channelTitle"],
                    Channel_Id=item["snippet"]["channelId"],
                    Video_Id=item['id'],
                    Title=item["snippet"]["title"],
                    Tags=item['snippet'].get("tags"),
                    Thumbnail=item["snippet"]["thumbnails"]["default"]["url"],
                    Description=item['snippet'].get("description"),
                    Published_Date=item["snippet"]["publishedAt"],
                    Duration=item['contentDetails']['duration'],
                    Views=item['statistics'].get("viewCount"),
                    Likes=item['statistics'].get("likeCount"),
                    Comments=item['statistics'].get('commentCount'),
                    Favourite_Count=item['statistics'].get('favoriteCount'),
                    Definition=item['contentDetails']['definition'],
                    Caption_Status=item['contentDetails']['caption'])
            video_data.append(data)
    return video_data


#get Comment info
def get_comment_info(video_ids):
    Comment_data=[]
    try:
        for video_id in video_ids:
            request=yt.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()
            for item in response['items']:
                data=dict(Comment_Id=item['snippet']['topLevelComment']['id'],
                        Video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                        Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                Comment_data.append(data)
    except:
        pass
    return Comment_data

#Get Playlist Info
def get_playlist_info(channel_id):
    next_page_token=None
    All_data=[]
    while True:
        request=yt.playlists().list(
            part='snippet,contentDetails',
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response=request.execute()

        for item in response['items']:
            data=dict(Playlist_Id=item['id'],
                    Title=item['snippet']['title'],
                    Channel_Id=item['snippet']['channelId'],
                    Channel_Name=item['snippet']['channelTitle'],
                    PublishedAt=item['snippet']['publishedAt'],
                    Video_Count=item['contentDetails']['itemCount'])
            All_data.append(data)
        next_page_token=response.get('nextPageToken')    
        if next_page_token is None:
            break
    return All_data    

#Upload to Mongo
client=pymongo.MongoClient("mongodb://localhost:27017")
db=client['Youtube_data']

def channel_details(channel_id):
    ch_details=get_channel_info(channel_id)
    pl_details=get_playlist_info(channel_id)
    vi_ids=get_videos_ids(channel_id)
    vi_details=get_video_info(vi_ids)
    com_details=get_comment_info(vi_ids)
    coll1=db['channel_details']
    
    coll1.insert_one({"channel_information":ch_details,
                      "playlist_information":pl_details,
                      "video_information":vi_details,
                      "comment_information":com_details
                      })
    return "Uploaded Successfully!"

#Table Creation for channels,playlists,videos and comments
def channels_table():
    mydb=psycopg2.connect(host="localhost",
                        user='postgres',
                        password='root',
                        database='youtube_data1',
                        port='5432')
    cursor=mydb.cursor()

    drop_query='''drop table if exists channels'''
    cursor.execute(drop_query)
    mydb.commit()

    try:
        create_query='''create table if not exists channels(Channel_Name varchar(100),
                                                            Channel_Id varchar(80) primary key,
                                                            Subscribers bigint,
                                                            Views bigint,
                                                            Total_Videos int,
                                                            Channel_Description text,
                                                            Playlist_Id varchar(80))'''
        cursor.execute(create_query)
        mydb.commit()
    except:
        print("Channel Table already created!")    

    ch_list=[]
    db=client['Youtube_data']
    coll1=db['channel_details']

    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data['channel_information'])
    df=pd.DataFrame(ch_list)

    for index,row in df.iterrows():
        insert_query='''insert into channels (Channel_Name,
                                            Channel_Id,
                                            Subscribers,
                                            Views,
                                            Total_Videos
                                            ,Channel_Description
                                            ,Playlist_Id)
                                            values(%s,%s,%s,%s,%s,%s,%s)'''
        values=(row['Channel_Name'],
                row['Channel_Id'],
                row['Subscribers'],
                row['Views'],
                row['Total_Videos'],
                row['Channel_Description'],
                row['Playlist_Id'])
        
        try:
            cursor.execute(insert_query,values)
            mydb.commit()
        except:
            print('Channels values are already inserted')        
            

def playlists_table():
    mydb=psycopg2.connect(host="localhost",
                        user='postgres',
                        password='root',
                        database='youtube_data1',
                        port='5432')
    cursor=mydb.cursor()

    drop_query='''drop table if exists playlists'''
    cursor.execute(drop_query)
    mydb.commit()

    create_query='''create table if not exists playlists( Playlist_Id varchar(100) primary key,
                                                        Title varchar(100),
                                                        Channel_Id varchar(100),
                                                        Channel_Name varchar(100),
                                                        PublishedAt timestamp,
                                                        Video_Count int)'''
    cursor.execute(create_query)
    mydb.commit()   
    
    pl_list=[]
    db=client['Youtube_data']
    coll1=db['channel_details']

    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data['playlist_information'])):
            pl_list.append(pl_data['playlist_information'][i])
    df1=pd.DataFrame(pl_list)
    
    for index,row in df1.iterrows():
        insert_query='''insert into playlists (Playlist_Id,
                                            Title,
                                            Channel_Id,
                                            Channel_Name,
                                            PublishedAt,
                                            Video_Count)
                                            values(%s,%s,%s,%s,%s,%s)'''
        values=(row['Playlist_Id'],
                row['Title'],
                row['Channel_Id'],
                row['Channel_Name'],
                row['PublishedAt'],
                row['Video_Count'])
        cursor.execute(insert_query,values)
        mydb.commit()   

        

#Table creation for videos
def videos_table():
        mydb=psycopg2.connect(host="localhost",
                        user='postgres',
                        password='root',
                        database='youtube_data1',
                        port='5432')
        cursor=mydb.cursor()

        drop_query='''drop table if exists videos'''
        cursor.execute(drop_query)
        mydb.commit()

        create_query='''create table if not exists videos(Channel_Name varchar(100),
                        Channel_Id varchar(100),
                        Video_Id varchar(30) primary key,
                        Title varchar(150),
                        Tags text,
                        Thumbnail varchar(200),
                        Description text,
                        Published_Date timestamp,
                        Duration interval,
                        Views bigint,
                        Likes bigint,
                        Comments int,
                        Favourite_Count int,
                        Definition varchar(10),
                        Caption_Status varchar(50))'''
        cursor.execute(create_query)
        mydb.commit()   

        vi_list=[]
        db=client['Youtube_data']
        coll1=db['channel_details']

        for vi_data in coll1.find({},{"_id":0,"video_information":1}):
                for i in range(len(vi_data['video_information'])):
                        vi_list.append(vi_data['video_information'][i])
                df2=pd.DataFrame(vi_list)


        for index,row in df2.iterrows():
                insert_query='''insert into videos(Channel_Name,
                                                Channel_Id,
                                                Video_Id,
                                                Title,
                                                Tags,
                                                Thumbnail,
                                                Description,
                                                Published_Date,
                                                Duration,
                                                Views,
                                                Likes,
                                                Comments,
                                                Favourite_Count,
                                                Definition,
                                                Caption_Status)
                                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                values=(row['Channel_Name'],
                        row['Channel_Id'],
                        row['Video_Id'],
                        row['Title'],
                        row['Tags'],
                        row['Thumbnail'],
                        row['Description'],
                        row['Published_Date'],
                        row['Duration'],
                        row['Views'],
                        row['Likes'],
                        row['Comments'],
                        row['Favourite_Count'],
                        row['Definition'],
                        row['Caption_Status'])
                cursor.execute(insert_query,values)
                mydb.commit() 
      


#Table Creation for comments
def comments_table():
        mydb=psycopg2.connect(host="localhost",
                                user='postgres',
                                password='root',
                                database='youtube_data1',
                                port='5432')
        cursor=mydb.cursor()

        drop_query='''drop table if exists comments'''
        cursor.execute(drop_query)
        mydb.commit()

        create_query='''create table if not exists comments(Comment_Id varchar(100) primary key,
                        Video_Id varchar(50),
                        Comment_Text text,
                        Comment_Author varchar(150),
                        Comment_Published timestamp)'''
        cursor.execute(create_query)
        mydb.commit()   

        com_list=[]
        db=client['Youtube_data']
        coll1=db['channel_details']

        for com_data in coll1.find({},{"_id":0,"comment_information":1}):
                for i in range(len(com_data['comment_information'])):
                        com_list.append(com_data['comment_information'][i])
        df3=pd.DataFrame(com_list)

        for index,row in df3.iterrows():
                insert_query='''insert into comments (Comment_Id,
                                                Video_Id,
                                                Comment_Text,
                                                Comment_Author,
                                                Comment_Published)
                                                values(%s,%s,%s,%s,%s)'''
                values=(row['Comment_Id'],
                        row['Video_Id'],
                        row['Comment_Text'],
                        row['Comment_Author'],
                        row['Comment_Published'])
                cursor.execute(insert_query,values)
                mydb.commit()


def tables():
    channels_table()
    playlists_table()
    videos_table()
    comments_table()
    return "Tables created successfully"

def show_channels_table():
    ch_list=[]
    db=client['Youtube_data']
    coll1=db['channel_details']
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data['channel_information'])
    df=st.dataframe(ch_list)
    return df

def show_playlists_table():
    pl_list=[]
    db=client['Youtube_data']
    coll1=db['channel_details']
    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data['playlist_information'])):
            pl_list.append(pl_data['playlist_information'][i])
    df1=st.dataframe(pl_list)
    return df1

def show_videos_table():
    vi_list=[]
    db=client['Youtube_data']
    coll1=db['channel_details']
    for vi_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data['video_information'])):
            vi_list.append(vi_data['video_information'][i])
    df2=st.dataframe(vi_list)
    return df2

def show_comments_table():
    com_list=[]
    db=client['Youtube_data']
    coll1=db['channel_details']
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
            for i in range(len(com_data['comment_information'])):
                    com_list.append(com_data['comment_information'][i])
    df3=st.dataframe(com_list)
    return df3


# Set page configuration
st.set_page_config(
    page_title="YouTube Data App",
    page_icon=":clapper:",
    layout="wide",  # You can customize the layout as per your requirement
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("Youtube Data Harvesting and Warehousing")
    st.header("Skill take away")
    st.caption("🚀Python Scripting")
    st.caption("🚀Data Collection")
    st.caption("🚀Mongo DB")
    st.caption("🚀API Integration")
    st.caption("🚀Data Management using MongoDB and SQL")

channel_id = st.text_input("Enter the Channel Id")

if st.button("Collect and Store data"):
    ch_ids = []
    db = client['Youtube_data']
    coll1 = db['channel_details']
    for ch_data in coll1.find({}, {'_id': 0, "channel_information": 1}):
        ch_ids.append(ch_data["channel_information"]["Channel_Id"])
    if channel_id in ch_ids:
        st.success("Channel Details of the given Channel Id already exist")
    else:
        insert = channel_details(channel_id)
        st.success(insert)

if st.button("Migrate to SQL"):
    Table = tables()
    st.success(Table)

show_tables = st.radio("Select the Table to View", ("Channels🎬", "Playlist📺", "Videos🎥", "Comments💬"))


if show_tables=="CHANNELS":  
    show_channels_table()      
elif show_tables=="PLAYLISTS":  
    show_playlists_table()      
elif show_tables=="VIDEOS":  
    show_videos_table()      
elif show_tables=="COMMENTS":  
    show_comments_table() 

#SQL Connection
mydb=psycopg2.connect(host="localhost",
                        user='postgres',
                        password='root',
                        database='youtube_data1',
                        port='5432')
cursor=mydb.cursor()
question=st.selectbox("Select Your Question",("1. What are the names of all the videos and their corresponding channels?",
                                              "2. Which channel has the most number of videos, and how much do they have?",
                                              "3. What are the top 10 most viewed videos and their corresponding channel names?",
                                              "4. How many comments were made on each video, and what are their corresponding video names?",
                                              "5. Which videos have the most number of likes, and what are their corresponding channel names?",
                                              "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                                              "7. What is the total number of views for each channel, and what are their channel names?",
                                              "8. What are the names of all the channels that have published videos in the year 2022",
                                              "9. What is the average duration of all the videos in each channel, and what are their corresponding channel names?",
                                              "10. Which videos have the highest number of comments, and what are their corresponding channel names?"))
if question[0:2]=='1.':
    query1='''select title as videos,channel_name as channelname from videos'''
    cursor.execute(query1)
    mydb.commit()
    t1=cursor.fetchall()
    df=pd.DataFrame(t1,columns=['video tile','channel name'])
    st.write(df)
elif question[0:2]=='2.':
    query2='''select channel_name as channelname,total_videos as no_videos from channels
          order by total_videos desc'''   
    cursor.execute(query2)
    mydb.commit()
    t2=cursor.fetchall()
    df2=pd.DataFrame(t2,columns=['channel name','No of Videos'])
    st.write(df2)
elif question[0:2]=='3.':
    query3='''select views as views,channel_name as channelname,title as videotitle from videos where views is not null
          order by views desc limit 10'''   
    cursor.execute(query3)
    mydb.commit()
    t3=cursor.fetchall()
    df3=pd.DataFrame(t3,columns=['Views','Channel name','Video title'],index=[1,2,3,4,5,6,7,8,9,10])
    st.write(df3)  
elif question[0:2]=='4.':
    query4='''select comments as no_comments,title as videotitle from videos where comments is not null'''   
    cursor.execute(query4)
    mydb.commit()
    t4=cursor.fetchall()
    df4=pd.DataFrame(t4,columns=['No of Comments','Video Title'])
    st.write(df4)
elif question[0:2]=='5.':
    query5='''select title as videotitle, channel_name as channelname,likes as likecount from videos
            where likes is not null order by likes desc'''   
    cursor.execute(query5)
    mydb.commit()
    t5=cursor.fetchall()
    df5=pd.DataFrame(t5,columns=['Video Title','Channel Name','Like Count'])
    st.write(df5)
elif question[0:2]=='6.':
    query6='''select likes as likecount,title as videotitle from videos'''   
    cursor.execute(query6)
    mydb.commit()
    t6=cursor.fetchall()
    df6=pd.DataFrame(t6,columns=['Like Count','Video Title'])
    st.write(df6)
elif question[0:2]=='7.':
    query7='''select channel_name as channelname,views as totalviews from channels'''   
    cursor.execute(query7)
    mydb.commit()
    t7=cursor.fetchall()
    df7=pd.DataFrame(t7,columns=['Channel Name','Total Views'])
    st.write(df7)
elif question[0:2]=='8.':
    query8='''select title as video_title,published_date as videorelease,channel_name as channelname from videos
            where extract(year from published_date)=2022'''   
    cursor.execute(query8)
    mydb.commit()
    t8=cursor.fetchall()
    df8=pd.DataFrame(t8,columns=['Video Title','Published Date','Channel Name'])
    st.write(df8)
elif question[0:2]=='9.':
    query9='''select channel_name as channelname,AVG(duration) as averageduration from videos group by channel_name'''   
    cursor.execute(query9)
    mydb.commit()
    t9=cursor.fetchall()
    df9=pd.DataFrame(t9,columns=['Channel Name','Average Duration'])
    T9=[]
    for index,row in df9.iterrows():
        channel_title=row['Channel Name']
        average_duration=row['Average Duration']
        average_duration_str=str(average_duration)
        T9.append(dict(channeltitle=channel_title,avgduration=average_duration_str))
    df1=pd.DataFrame(T9)
    st.write(df9)
elif question[0:2]=='10':    
    query10='''select title as video_title,channel_name as channelname,comments as comments from videos
            where comments is not null order by comments desc'''   
    cursor.execute(query10)
    mydb.commit()
    t10=cursor.fetchall()
    df10=pd.DataFrame(t10,columns=['Video Title','Published Date','Channel Name'])
    st.write(df10)

    