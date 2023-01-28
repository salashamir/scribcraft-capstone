from app import db
from models import User, Scrib, Comment


db.drop_all()
db.create_all()

user1 = User(username="gregoryhunt",
             email="greghunt3728472@gmail.com", password="dewn437438fryf!")
user2 = User(username="carneylori	",
             email="bryantrachel@yahoo.com",
             image_url="https://randomuser.me/api/portraits/women/33.jpg", password="eiufeirufhe7483743")
user3 = User(username="thompsonadam",
             email="crobinson@young.com", image_url="https://randomuser.me/api/portraits/men/99.jpg	", password="3483bfurfb347!!!")
user4 = User(username="steelenatalie",
             email="karenbates@hotmail.com", image_url="https://randomuser.me/api/portraits/women/94.jpg", password="48fnrufryeub387!28")
user5 = User(username="clewis",
             email="tiffanygarcia@hotmail.com", password="batoutbatout23723")
user6 = User(username="william80",
             email="rodriguezkaren@gmail.com", image_url="https://randomuser.me/api/portraits/men/73.jpg", password="mycoolpassword84734376")

db.session.add_all([user1, user2, user3, user4, user5, user6])
db.session.commit()

scrib1 = Scrib(title="Penitentiary ghosts", prompt="An innocent man imprisoned and sentenced to death on false charges seeks to escape from a high security prison haunted by the ghosts of those who have been executed on death row.", scrib_text="The innocent man, Joshua, is a formerly average man living out his days in the small town of New Haven. He is an introspective individual with a kind spirit who had been swept up and wrongfully convicted in a corrupt system without evidence. Having exhausted all of his legal options, he finds himself facing death row amidst an oppressive atmosphere filled with fear and hopelessness. His motivation is to simply stay alive long enough for the truth to be discovered or for some outside intervention to save him from unwarranted execution at the hands of malicious forces that have taken away his freedom.\n Josh's primary friend on death row is fellow prisoner Jaxon, who has stayed true to Joshua through thick and thin ever since they were both sent down there five years ago. However their friendship can only provide so much comfort given the circumstances as dark specters linger throughout the prison late at night giving warnings that those unfortunate victims before them never made it beyond these walls alive.\n The antagonist in this story would be Judge Hartman –– a cold hearted career politician that sent Joshua away without even batting an eye believing fully well that right or wrong justice was being served which also furthered her political ambitions as punishment was swift and severe under her watchful eye. Her motives are rooted more so in vanity than righteousness as she attempts to further secure her position within society by letting power blindly rule over what little common sense she possesses when it comes to judging others based solely on circumstantial evidence.\n The inciting incident occurs when tensions finally reach their peak inside the prison walls due in no small part due largely to unfair restrictions placed upon prisoners by severely overbearing guards tasked specifically with keeping order inside such disconcerting surroundings; however things take yet another strange turn when multiple inmates begin reporting ghost sightings filling everyone with dread about just how unchecked murder may lie dormant within these halls after decades have gone by seemingly forgotten or ignored altogether until now....rising action follows thereafter as strange events continue gathering pace around elements once thought impossible but making complete sense otherwise due to what lies underneath each drama unfolding practically day by day ultimately leading us right back into where we began –– only this time it becomes clear just how much trouble our protagonist may truly find himself well past redemption should help not arrive soon enough...the conclusion brings closure albeit bittersweet as certain revelations come forth though revelations which could easily undo any one faith despite many trials had.....in other words while there will always be evil lurking amongst us sometimes innocence still stands tall even amidst darkness…..", user_id=user1.id)

scrib2 = Scrib(title="From galaxy to earth", prompt="An intrepid explorer from an alien planet journeys to Earth to recover an ancient artifact left behind by his ancestors long ago.", scrib_text="""The main character is an intrepid explorer from a distant alien planet. His name is Zax and he has been sent on a mission to recover an ancient artifact that was left behind by his ancestors long ago. He is motivated by the desire to bring back something of value to his people, and also out of curiosity as he wants to know more about the history of his species. 

Other characters in this story include: 
- Captain Krenn, Zax's commanding officer who gave him the mission and will be monitoring his progress from afar; 
- Professor Venn, an expert on ancient artifacts who helps Zax with research; 
- Jorin, a human guide who helps Zax navigate Earth's terrain; 
- And lastly there is The Collector - a mysterious figure whose motives are unknown but appears intent on stopping Zax at all costs.  

The story begins with an inciting incident when Captain Krenn assigns Zax the task of recovering the artifact from Earth. After some initial research with Professor Venn, they discover clues pointing them towards its location in South America. With Jorin’s help navigating through dense jungles and treacherous mountainsides, they eventually make it close enough for their sensors to detect its energy signature emanating from deep within a hidden temple complex guarded by strange creatures unlike anything seen before on Earth or elsewhere in space! As soon as they enter however they come face to face with The Collector - determined not only to keep them away from their goal but also revealing himself as one of their own race! It turns out that he had been living among humans for centuries after being exiled for crimes against their people many years ago and now seeks revenge against those responsible for taking away everything he ever knew or loved…  

With no other choice than fight or flight, our heroes battle fiercely against The Collector until finally managing to gain access into the inner sanctum whereupon retrieving the artifact triggers some kind of reaction causing massive tremors throughout the entire temple complex! In order escape destruction our heroes must work together using all their skills combined while racing against time before it collapses around them! In doing so however they manage not only survive but also take back what was lost so long ago thus fulfilling both theirs and Captain Krenn’s missions successfully…""", user_id=user3.id)

scrib3 = Scrib(title="Those who hunger below", prompt="Oliver, an orphan, discovers a subterranean tunnel under his orphanage that leads to a trapped cannibal civilization.", scrib_text="""Oliver is an orphaned young man who lives in a small town with his fellow orphans. He has always been curious about the world around him, and he loves to explore. One day while exploring the grounds of the orphanage, Oliver discovers a hidden entrance leading to a subterranean tunnel. The tunnel leads to an underground civilization that has been trapped there for centuries by powerful magic spells. This civilization is made up of cannibals who have resorted to eating each other in order to survive their long imprisonment beneath the earth's surface.

The main characters include: 
Oliver - A brave and curious young man who finds himself on an unexpected adventure when he discovers the secret tunnel under his orphanage; motivated by curiosity and a desire for knowledge 
Finn - An old hermit living near Oliver's orphanage; Finn helps guide Oliver on his journey, providing wisdom and advice along the way 
Rikki - A member of the cannibalistic society below ground; Rikki befriends Oliver and helps him understand more about this mysterious culture 
The Antagonist: 
Grimm – Leader of the cannibalistic society below ground; Grimm seeks revenge against those responsible for trapping them down there all these years, using any means necessary including violence if needed; motivated by anger and hatred towards those responsible for their suffering  
Beginning: After discovering a strange entrance leading into what appears to be some kind of underground tunnel, Oliver decides to investigate further despite warnings from Finn not too. Following it deep into its depths, he eventually comes across an entire civilization that had been trapped beneath Earth’s surface due hundreds of years ago by powerful magical forces. This group consists entirely out of cannibals that have resorted to consuming one another just so they can survive their long imprisonment within this dark abyssal realm. When confronted by Grimm – leader of this savage tribe – Oliver quickly realizes that he must find away out before it’s too late or else suffer at their hands as well!  

Rising Action: With help from Rikki–a friendly member among Grimms people–Oliver begins searching through ancient texts looking for clues regarding how they might escape this prison-like place without being detected or harmed in anyway possible . As time passes however , Grimm becomes increasingly suspicious as many members are beginning question why someone like oliver would ever come down here amongst them . Despite numerous attempts , no solution seems forthcoming until finally after days upon days spent researching together , they stumble across something which could""", user_id=user6.id)

scrib4 = Scrib(title="The time traveling patient", prompt="An injured man recovering from a leg injury in a hospital ward discovers that at night he is able to travel back in time to different eras as a patient.", scrib_text="""The main character of the story is John, a young man in his mid-20s who has recently been admitted to a hospital ward after suffering an injury to his leg. He is eager to recover and get back on with his life, but he soon discovers that at night he can travel back in time as a patient in different eras. 

John meets several other characters during his travels, including Doctor Johnson, an elderly doctor from the 19th century who takes him under her wing and helps him understand what is happening; Nurse Mary, a kind nurse from the same era whose compassion for patients inspires John; and Abigail, another patient from the past who shares similar experiences with John. 

The antagonist of this story is Dr. Smithson - an ambitious scientist from present day whose goal it is to find out how John's ability works so that he can use it for personal gain. He uses unethical methods such as manipulation and intimidation to try and force John into revealing more about himself than he wants too. 

The inciting incident occurs when one night while recovering in the hospital ward, John suddenly finds himself transported back in time as a patient at Doctor Johnson's clinic. From there we follow him through various adventures across different eras where he learns more about why this strange phenomenon is happening to him and what purpose it serves - all while trying desperately not be discovered by Dr Smithson or fall victim to any of his schemes. As rising action builds throughout each journey into history we eventually reach a climax when Dr Smithson finally catches up with them both just before they are able return home safely once again - only for us then discover that their journeys have allowed them access something far greater than either could have imagined... 

In conclusion we see that despite all odds being against them both they were able unlock some of life’s greatest mysteries together – allowing them both peace within themselves knowing that no matter what happens next they will always have each other’s support along the way!""", user_id=user5.id)

db.session.add_all([scrib1, scrib2, scrib3, scrib4])
db.session.commit()

comment1 = Comment(comment_text="Great idea! I love the concept and think this would make a tremendous series!",
                   user_id=user3.id, scrib_id=scrib3.id)
comment2 = Comment(comment_text="I wonder if you could include some more fantasy elements in this?",
                   user_id=user6.id, scrib_id=scrib3.id)
comment3 = Comment(comment_text="These characters maybe could have some more adventurous traits",
                   user_id=user2.id, scrib_id=scrib1.id)

db.session.add_all([comment1, comment2, comment3])
db.session.commit()
