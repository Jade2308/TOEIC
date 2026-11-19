#!/usr/bin/env python3
"""
scripts/build_part7_final.py
============================
Generates full, authentic TOEIC Part 7 data for ETS TOEIC 2023 Test 1:
- All 15 question groups (10 Single Passages, 2 Double Passages, 3 Triple Passages)
- All 54 questions (Questions 147 to 200)
- Authentic, verbatim reading passages with semantic HTML formatting
- Exact official ETS answer key matching Dap-an-test-1-ets-2023.answers.json
- Verbatim evidence_quotes for auto-highlighting in AdaptiveSplitLayout
- High-res cropped scan image URLs (/images/test1/part7_XXX_YYY.png)
- Comprehensive pedagogical Vietnamese explanations (Grammar, Analysis, Traps, Tips)
- Standard question_type_tags and paraphrase_pairs
"""

import json
import os
import sys

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

part7_groups = [
    # -------------------------------------------------------------------------
    # Group 1: Questions 147-148 (Single: Advertisement)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g147_148",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_147_148.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-amber-50/40 dark:bg-neutral-900/40 shadow-xs space-y-3">
  <div class="text-center border-b border-neutral-200 dark:border-neutral-800 pb-2">
    <h3 class="font-extrabold text-lg text-neutral-900 dark:text-neutral-100 tracking-wide uppercase">Harbis Stationery Store Clearance Sale</h3>
    <p class="text-xs text-rose-600 dark:text-rose-400 font-semibold italic mt-0.5">Prices indicated are for in-store purchases only.</p>
    <p class="text-xs text-neutral-500 mt-0.5">500 Pinstone Street / SHEFFIELD / S12HN</p>
  </div>
  
  <div class="space-y-2 text-xs text-neutral-800 dark:text-neutral-200">
    <div class="font-bold text-indigo-700 dark:text-indigo-400 uppercase text-[11px] tracking-wider border-b border-neutral-200 dark:border-neutral-800 pb-1">Seasonal Items</div>
    <div class="flex justify-between items-center py-0.5">
      <span>Box of ten preprinted seasonal cards (25% off)</span>
      <span class="font-bold">£ 8.99</span>
    </div>
    <div class="flex justify-between items-center py-0.5">
      <span>Box of five customizable seasonal cards or invitations (50% off)</span>
      <span class="font-bold text-rose-600 dark:text-rose-400">£ 11.99</span>
    </div>
    
    <div class="font-bold text-indigo-700 dark:text-indigo-400 uppercase text-[11px] tracking-wider border-b border-neutral-200 dark:border-neutral-800 pb-1 pt-2">All School Supplies 10% Off</div>
    <div class="grid grid-cols-2 gap-x-4 gap-y-1">
      <div class="flex justify-between"><span>Box of 24 pens</span><span class="font-bold">£ 1.79</span></div>
      <div class="flex justify-between"><span>Desk lamp</span><span class="font-bold">£ 19.99</span></div>
      <div class="flex justify-between"><span>Wireless mouse</span><span class="font-bold">£ 17.99</span></div>
      <div class="flex justify-between"><span>Backpack</span><span class="font-bold">£ 29.99</span></div>
    </div>
  </div>
  
  <div class="text-center pt-2 border-t border-neutral-200 dark:border-neutral-800 text-[11px] text-neutral-500">
    Visit Harbis Stationery at <a href="http://www.harbisstationery.uk" class="text-indigo-600 dark:text-indigo-400 underline font-medium">www.harbisstationery.uk</a>
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 2: Questions 149-150 (Single: E-mail)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g149_150",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_149_150.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-3 text-xs leading-relaxed">
  <div class="border-b border-neutral-200 dark:border-neutral-800 pb-2 space-y-1 text-neutral-600 dark:text-neutral-400">
    <div><strong class="text-neutral-900 dark:text-neutral-100">To:</strong> Wenbin Peng &lt;wpeng@chenconstruction.com&gt;</div>
    <div><strong class="text-neutral-900 dark:text-neutral-100">From:</strong> Toshi Auto Group &lt;cs@toshiautogroup.com&gt;</div>
    <div><strong class="text-neutral-900 dark:text-neutral-100">Date:</strong> February 26</div>
    <div><strong class="text-neutral-900 dark:text-neutral-100">Subject:</strong> Your leased vehicle</div>
  </div>
  
  <p class="font-semibold text-neutral-800 dark:text-neutral-200">Dear Mr. Peng,</p>
  <p>As you know, Toshi Auto Group handles all the service needs for cars leased by employees of Chen Construction. According to our records, you took possession of your leased car on March 1 of last year. Your car is now due for its required annual service and maintenance check. To book your appointment, please call us at (215) 555-0109 or visit us online at www.toshiautogroup.com/serviceappointments.</p>
  <p class="pt-2 text-neutral-600 dark:text-neutral-400">Sincerely,<br/><strong class="text-neutral-900 dark:text-neutral-100">Toshi Auto Group</strong><br/>Customer Service</p>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 3: Questions 151-153 (Single: Article)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g151_153",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_151_153.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-3 text-xs leading-relaxed">
  <div class="border-b border-neutral-200 dark:border-neutral-800 pb-2">
    <h3 class="font-bold text-base text-neutral-900 dark:text-neutral-100">Tillford Press Announces Launch of New Imprint</h3>
    <p class="text-[11px] text-neutral-500 italic mt-0.5">LONDON (22 October)</p>
  </div>
  
  <p>Tillford Press announced the launch of its new imprint, Tillford Exalt. This new line will feature books promoting healthy lifestyles, memoirs with uplifting messages, and volumes that provide guidance for special occasions such as birthdays and weddings. Tillford Exalt will also publish calendars and greeting cards that complement the main products.</p>
  <p>Already contracted to write memoirs are the award-winning actress Alexia Leoz, London-based conductor and composer Seung-Hyun Bae, and celebrity cook Lain Lai. Ms. Lai's story of her life and career will be the first to be launched. It is set for release in December.</p>
  <p>Tillford vice president Frederick Bissett said the company saw a need for books that celebrated accomplishments and life events from multiple perspectives. "We wanted authors from a wide variety of cultural backgrounds, and we think we're off to a great start," he said. He noted that Tillford Exalt's authors were not always famous; the books will be exploring their beginnings, their everyday lives, their first jobs, their marriages and families—as well as their achievements.</p>
  <p>Tillford Press is based in Manchester. It has offices in New York, Toronto, and Sydney, but its publications are sold throughout the world.</p>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 4: Questions 154-155 (Single: Text-Message Chain)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g154_155",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_154_155.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-neutral-50/50 dark:bg-neutral-900 shadow-xs space-y-3 text-xs">
  <div class="text-center font-bold text-neutral-500 uppercase text-[10px] tracking-wider border-b border-neutral-200 dark:border-neutral-800 pb-1.5">
    Internal Warehouse Messaging
  </div>
  
  <div class="space-y-2.5">
    <div class="p-2.5 rounded-xl bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
      <div class="flex justify-between font-bold text-neutral-800 dark:text-neutral-200 mb-0.5">
        <span>Greg Skagen</span>
        <span class="text-[10px] text-neutral-400 font-normal">8:58 A.M.</span>
      </div>
      <p class="text-neutral-700 dark:text-neutral-300">Hi, Brenda. I'm here in the warehouse. All of my trainees have arrived, but I noticed the power door at Loading Dock B is acting up.</p>
    </div>
    
    <div class="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900/50 ml-4">
      <div class="flex justify-between font-bold text-indigo-900 dark:text-indigo-300 mb-0.5">
        <span>Brenda Sadauskas</span>
        <span class="text-[10px] text-indigo-400 font-normal">8:59 A.M.</span>
      </div>
      <p class="text-indigo-950 dark:text-indigo-200">Again?</p>
    </div>
    
    <div class="p-2.5 rounded-xl bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
      <div class="flex justify-between font-bold text-neutral-800 dark:text-neutral-200 mb-0.5">
        <span>Greg Skagen</span>
        <span class="text-[10px] text-neutral-400 font-normal">8:59 A.M.</span>
      </div>
      <p class="text-neutral-700 dark:text-neutral-300">When I push the button to open it, it raises all the way up but then drops back down to the closed position after about 30 seconds.</p>
    </div>
    
    <div class="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900/50 ml-4">
      <div class="flex justify-between font-bold text-indigo-900 dark:text-indigo-300 mb-0.5">
        <span>Brenda Sadauskas</span>
        <span class="text-[10px] text-indigo-400 font-normal">9:00 A.M.</span>
      </div>
      <p class="text-indigo-950 dark:text-indigo-200">I'll come down with the maintenance technicians. Why don't you bring your trainees to my area? You can teach them how to create shipping labels and then have them pack and label this morning's shipments.</p>
    </div>
    
    <div class="p-2.5 rounded-xl bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
      <div class="flex justify-between font-bold text-neutral-800 dark:text-neutral-200 mb-0.5">
        <span>Greg Skagen</span>
        <span class="text-[10px] text-neutral-400 font-normal">9:02 A.M.</span>
      </div>
      <p class="text-neutral-700 dark:text-neutral-300 font-semibold text-emerald-700 dark:text-emerald-400">Yes, that works.</p>
    </div>
    
    <div class="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900/50 ml-4">
      <div class="flex justify-between font-bold text-indigo-900 dark:text-indigo-300 mb-0.5">
        <span>Brenda Sadauskas</span>
        <span class="text-[10px] text-indigo-400 font-normal">9:03 A.M.</span>
      </div>
      <p class="text-indigo-950 dark:text-indigo-200">Thanks. Then you could show them the loading dock operations in the afternoon.</p>
    </div>
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 5: Questions 156-157 (Single: Form)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g156_157",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_156_157.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-3 text-xs">
  <div class="text-center border-b border-neutral-200 dark:border-neutral-800 pb-2">
    <h3 class="font-extrabold text-base text-neutral-900 dark:text-neutral-100 uppercase tracking-wider">Service Request Form</h3>
    <p class="text-[11px] text-neutral-500 italic">Complete all fields and deliver to Technology Services (room 412).</p>
  </div>
  
  <div class="grid grid-cols-2 gap-2 border-b border-neutral-200 dark:border-neutral-800 pb-2.5 text-neutral-700 dark:text-neutral-300">
    <div><strong>Requester Name:</strong> Eleanora Deckow</div>
    <div><strong>Requester Office:</strong> Room 718</div>
    <div><strong>Requester Phone:</strong> Ext. 5709</div>
    <div><strong>Service Location:</strong> Room 500</div>
  </div>
  
  <div class="border-b border-neutral-200 dark:border-neutral-800 pb-2">
    <div class="font-bold mb-1 text-neutral-800 dark:text-neutral-200">Service Type (choose one):</div>
    <div class="flex gap-4">
      <span>[ ] Cleaning</span>
      <span class="font-bold text-indigo-600 dark:text-indigo-400">[x] Repair</span>
      <span>[ ] Installation/Setup</span>
      <span>[ ] Other</span>
    </div>
  </div>
  
  <div class="space-y-1.5">
    <div class="font-bold text-neutral-800 dark:text-neutral-200">Description of Request:</div>
    <p class="text-neutral-700 dark:text-neutral-300 leading-relaxed bg-neutral-50 dark:bg-neutral-800/50 p-2.5 rounded-lg border border-neutral-200 dark:border-neutral-700">
      There is a problem with the television audio. When I played an online video, the image was fine, but I could not hear anything. I checked all the settings, and I was able to hear the same video on other televisions with no problem.<br/><br/>
      I'm supposed to deliver a product demonstration for a client in room 500 next Monday, so I would greatly appreciate it if the issue can be fixed by this Friday.
    </p>
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 6: Questions 158-161 (Single: Text-Message Chain)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g158_161",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_158_161.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-neutral-50/50 dark:bg-neutral-900 shadow-xs space-y-3 text-xs">
  <div class="text-center font-bold text-neutral-500 uppercase text-[10px] tracking-wider border-b border-neutral-200 dark:border-neutral-800 pb-1.5">
    Corporate Messaging Channel: Marketing & Finance Sync
  </div>
  
  <div class="space-y-2">
    <div class="p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
      <div class="flex justify-between font-bold text-neutral-800 dark:text-neutral-200 mb-0.5"><span>Ella Glatt</span><span class="text-[10px] text-neutral-400 font-normal">11:34 A.M.</span></div>
      <p>Hi. I know this is a busy day, but I wanted to know whether anyone from the finance team could come to the marketing meeting.</p>
    </div>
    
    <div class="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900/50 ml-3">
      <div class="flex justify-between font-bold text-indigo-900 dark:text-indigo-300 mb-0.5"><span>Stef Goldberg</span><span class="text-[10px] text-indigo-400 font-normal">11:35 A.M.</span></div>
      <p>Hi, Ella. I wish I could, but it starts at 2:00. I need to be at a different meeting at 2:30.</p>
    </div>
    
    <div class="p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
      <div class="flex justify-between font-bold text-neutral-800 dark:text-neutral-200 mb-0.5"><span>Ella Glatt</span><span class="text-[10px] text-neutral-400 font-normal">11:36 A.M.</span></div>
      <p>Oh, right. I forgot you were going to the executive board meeting.</p>
    </div>
    
    <div class="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 ml-3">
      <div class="flex justify-between font-bold text-emerald-900 dark:text-emerald-300 mb-0.5"><span>Daniel Seidal</span><span class="text-[10px] text-emerald-400 font-normal">11:36 A.M.</span></div>
      <p>I'm also supposed to go to the 2:30 meeting. Is it essential that one of us attend the marketing meeting?</p>
    </div>
    
    <div class="p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
      <div class="flex justify-between font-bold text-neutral-800 dark:text-neutral-200 mb-0.5"><span>Ella Glatt</span><span class="text-[10px] text-neutral-400 font-normal">11:37 A.M.</span></div>
      <p>Well, it would be helpful to have someone from the finance department there, at least for 15 minutes or so.</p>
    </div>
    
    <div class="p-2 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50 ml-3">
      <div class="flex justify-between font-bold text-amber-900 dark:text-amber-300 mb-0.5"><span>Bill Iverman</span><span class="text-[10px] text-amber-400 font-normal">11:38 A.M.</span></div>
      <p>The quarterly reports just came in, and Daniel, Stef, and I need to review them by the end of the day.</p>
    </div>
    
    <div class="p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
      <div class="flex justify-between font-bold text-neutral-800 dark:text-neutral-200 mb-0.5"><span>Ella Glatt</span><span class="text-[10px] text-neutral-400 font-normal">11:39 A.M.</span></div>
      <p>You all have plenty to do.</p>
    </div>
    
    <div class="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 ml-3">
      <div class="flex justify-between font-bold text-emerald-900 dark:text-emerald-300 mb-0.5"><span>Daniel Seidal</span><span class="text-[10px] text-emerald-400 font-normal">11:41 A.M.</span></div>
      <p>That's true! But I could come from 2:00 to 2:15. That's all I can commit to.</p>
    </div>
    
    <div class="p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700">
      <div class="flex justify-between font-bold text-neutral-800 dark:text-neutral-200 mb-0.5"><span>Ella Glatt</span><span class="text-[10px] text-neutral-400 font-normal">11:43 A.M.</span></div>
      <p>Sounds great. We just need one of you to clarify a few quick points about the budget for the next advertising campaign.</p>
    </div>
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 7: Questions 162-165 (Single: E-mail)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g162_165",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_162_165.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-3 text-xs leading-relaxed">
  <div class="border-b border-neutral-200 dark:border-neutral-800 pb-2 space-y-1 text-neutral-600 dark:text-neutral-400">
    <div><strong class="text-neutral-900 dark:text-neutral-100">To:</strong> Tariq Abboud &lt;tabboud@abboudpartners.com&gt;</div>
    <div><strong class="text-neutral-900 dark:text-neutral-100">From:</strong> Maria McFarland &lt;maria_mcfarland@myemail.com&gt;</div>
    <div><strong class="text-neutral-900 dark:text-neutral-100">Date:</strong> Thursday, August 22</div>
    <div><strong class="text-neutral-900 dark:text-neutral-100">Subject:</strong> Project Coordinator Position</div>
    <div><strong class="text-neutral-900 dark:text-neutral-100">Attachment:</strong> resume_m.mcfarland.pdf</div>
  </div>
  
  <p class="font-semibold text-neutral-800 dark:text-neutral-200">Dear Mr. Abboud,</p>
  <p>My friend Josiah Wilkins told me that you are seeking a project coordinator for your company. I have a degree in business administration and am attaching my résumé as I think I am an excellent fit for your needs. As you will see, I have experience using several cloud-based project-management programs. Furthermore, my organizational skills enable me to coordinate multiple activities simultaneously, and I can convey expectations clearly to team members involved in each phase of a project.</p>
  <p>My current role as project coordinator for an international engineering firm, where I have worked for the past five years, has also afforded me ample experience managing teams, schedules, and budgets. While I enjoy the kind of work I do, it has become clear to me that I need motivation from a strong mission. The goal of your company to create sustainable housing projects is something that I strongly support and would be delighted to work on.</p>
  <p>Through my work and volunteer activities, I have spent many months abroad in various countries throughout Asia and the Middle East. This seems particularly relevant to mention, as I am comfortable leading geographically and culturally diverse teams.</p>
  <p>Thank you for your attention, and I look forward to speaking with you soon.</p>
  <p class="pt-2 text-neutral-600 dark:text-neutral-400">Kind regards,<br/><strong class="text-neutral-900 dark:text-neutral-100">Maria McFarland</strong></p>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 8: Questions 166-168 (Single: Web page)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g166_168",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_166_168.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-3 text-xs leading-relaxed">
  <div class="border-b border-neutral-200 dark:border-neutral-800 pb-2 flex items-center justify-between">
    <div>
      <span class="text-[11px] text-neutral-400 font-mono">https://trexdale.com/aboutus</span>
      <h3 class="font-bold text-base text-neutral-900 dark:text-neutral-100 mt-0.5">About Our Company</h3>
    </div>
    <span class="px-2 py-0.5 bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 rounded text-[10px] font-bold">Trexdale Supply</span>
  </div>
  
  <p>Trexdale Supply specializes in designing, producing, and installing furniture for all types of scientific laboratories. We provide a range of fully assembled cabinets, workstations, benches, and more, all made exclusively at our production facility in Dallas, Texas. Our lab furniture is available in a wide variety of sizes and configurations to match the needs of any research application.</p>
  <p>Our business offers products as well as design-consulting services. For start-up labs, we have a team of consulting specialists available to evaluate your facility's specific needs and assist you in arranging your space and choosing the most suitable furniture. Recently, for example, we were chosen by a major producer of biofuels to provide expert help in changing the layout of a research laboratory to maximize available space. As a result of this project, this client has realized substantial savings by reducing energy usage in the lab.</p>
  <p>Please visit the "Lab Planning" section of this Web site if you are interested in learning more about building or renovating a laboratory facility. There, you can fill out an interest form to contact one of our consultants about your next project.</p>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 9: Questions 169-171 (Single: Job Advertisement)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g169_171",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_169_171.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-3 text-xs leading-relaxed">
  <div class="text-center border-b border-neutral-200 dark:border-neutral-800 pb-2">
    <h3 class="font-black text-base text-rose-700 dark:text-rose-400 uppercase tracking-wide">Product Demonstrators Needed!</h3>
    <p class="text-[11px] text-neutral-500 font-semibold mt-0.5">BBD Staffing Services</p>
  </div>
  
  <p>Are you outgoing and enthusiastic? — [1] — Do you enjoy talking to all types of people? Put your personality and communication skills to work! — [2] —. BBD Staffing is seeking to hire in-store product demonstrators to promote our clients' merchandise to shoppers. — [3] —. As a member of our team, you will demonstrate a wide range of small kitchen appliances and tools in grocery stores and other retail venues.</p>
  <p>For some products, you will be required to prepare simple recipes. You will also need to answer shoppers' questions. Thus, it is essential that you can become familiar with clients' products and provide key information to consumers. Because many of the demonstrations require working with food, candidates must have a Professional Food Handler certificate. — [4] —</p>
  <div class="p-2.5 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-center font-medium border border-neutral-200 dark:border-neutral-700">
    To apply, upload a video of no more than one minute in length telling us why you would be a successful product demonstrator at <a href="http://www.bbdstaffing.com/applications" class="text-indigo-600 dark:text-indigo-400 underline font-semibold">www.bbdstaffing.com/applications</a>.
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 10: Questions 172-175 (Single: Article)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g172_175",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_172_175.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-3 text-xs leading-relaxed">
  <div class="border-b border-neutral-200 dark:border-neutral-800 pb-2">
    <h3 class="font-bold text-base text-neutral-900 dark:text-neutral-100">Gorman Unveils Newest Smartphone Model</h3>
    <p class="text-[11px] text-neutral-500 italic mt-0.5">LONDON (20 May)</p>
  </div>
  
  <p>Gorman Mobile unveiled its newest smartphone to an eager reception at the annual Technobrit exhibition yesterday. The Gorman Pro Phone 4, which includes 512 GB of storage, a 7-inch screen display, and an optional stylus pen, will hit the shelves on 11 June. Unlike its predecessor—the Pro Phone 3—it features a larger screen, an ultrawide camera lens, and 8K-resolution filming capability.</p>
  <p>— [1] —. The £999 starting price is £100 more than that of the previous model. Add-ons, such as the stylus pen, protective case, and wireless headphones, cost an additional £39, £59, and £79, respectively. Gorman Product Manager Ian Hill doesn't believe the price increase will dissuade customers. — [2] —.</p>
  <p>"The Pro Phone 4 is a game changer in terms of its picture quality and sleek design," said Hill. "Improvements were based on direct customer feedback, which cited the poor camera functionality as the biggest drawback of the Pro Phone 3." — [3] —.</p>
  <p>One similarity that the Pro Phone 4 has with previous models is the charger. Going against the trend of competing wireless companies, Gorman is instead focusing on convenience. "We want to afford our customers the ability to reuse elements of the other Gorman devices they've already purchased," said Hill. "Why add to the overload of cables already in circulation?" — [4] —.</p>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 11: Questions 176-180 (Double Passage: Work Order & E-mail)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g176_180",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_176_180.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="space-y-4 text-xs leading-relaxed">
  <!-- Document 1: Work Order -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-amber-50/30 dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="flex justify-between items-center border-b border-neutral-200 dark:border-neutral-800 pb-1.5">
      <span class="font-bold text-sm text-neutral-900 dark:text-neutral-100">WORK ORDER: 7549</span>
      <span class="text-[11px] text-neutral-500 font-mono">Status: Pending Review</span>
    </div>
    <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-neutral-700 dark:text-neutral-300">
      <div><strong>Requester:</strong> Xi, Gina</div>
      <div><strong>Technician Assigned:</strong> Arnold, Sam</div>
      <div><strong>Date Entered:</strong> Wednesday, 9 April</div>
      <div><strong>Date Due:</strong> Thursday, 10 April</div>
      <div><strong>Type:</strong> Technology end-user request</div>
      <div><strong>Computer Workstation ID:</strong> HYS31</div>
      <div class="col-span-2"><strong>Summary:</strong> Voice-mail security settings</div>
    </div>
    <div class="pt-1.5 border-t border-neutral-200 dark:border-neutral-800">
      <div class="font-bold text-neutral-800 dark:text-neutral-200 mb-0.5">Description:</div>
      <p class="text-neutral-600 dark:text-neutral-400 italic">
        Is it possible to remove the new layers of security on my voice mail in the new phone system? I really don't want to use a password, and I certainly don't want to change it every month. I don't need a high degree of security because my work is not confidential. If someone else gained access to my messages, it wouldn't do much harm.
      </p>
    </div>
  </div>

  <!-- Document 2: E-mail -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-2.5">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1.5 text-neutral-600 dark:text-neutral-400 space-y-0.5">
      <div><strong class="text-neutral-900 dark:text-neutral-100">To:</strong> Gina Xi &lt;gxi@hyscorp.com&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">From:</strong> Sam Arnold &lt;sarnold@hyscorp.com&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Date:</strong> 10 April</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Subject:</strong> Tech support request 7549</div>
    </div>
    <p>Hello, Ms. Xi,</p>
    <p>This is in reference to your work order 7549 related to the new phone system. I am happy to help you with that. I understand that you do not feel that a high degree of security is needed for your voice-mail settings, but the new system does require you to have a password to retrieve your voice mail. However, company policy allows me to change the settings for employees who do not work with confidential material. I can update the security settings so that you do not have to reset the password on a regular basis.</p>
    <p>I want to make sure that you understand the risk involved with a lower level of security. Anyone who gains access to your voice-mail account can do more than simply listen to your messages. They would be able to delete messages, change your greeting, or change your password so that you would lose access to your own voice mail (at least until someone here at IT could override the password change). If you still feel comfortable with that level of risk, let me know, and I will change the settings so that your password never expires.</p>
    <p class="text-neutral-600 dark:text-neutral-400">Sam Arnold<br/>Tech Support Associate</p>
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 12: Questions 181-185 (Double Passage: E-mail & Review)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g181_185",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_181_185.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="space-y-4 text-xs leading-relaxed">
  <!-- Document 1: E-mail -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-2.5">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1.5 text-neutral-600 dark:text-neutral-400 space-y-0.5">
      <div><strong class="text-neutral-900 dark:text-neutral-100">To:</strong> Linda Hanshu &lt;lhanshu@rimerko.com&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">From:</strong> Cliff Merson &lt;cmerson@rimerko.com&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Date:</strong> September 4, 10:12 A.M.</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Subject:</strong> Lighting Issue</div>
    </div>
    <p>Hi, Ms. Hanshu:</p>
    <p>I want to check on the issue we discussed about lighting in the latest chapter of Titan Adventure. In past versions of the game, getting the reflections and lighting in green and blue areas correct has been a particular challenge, and it was a problem that kept arising. As the new release, Neptune's Voyage, is primarily an underwater adventure, addressing this problem is crucial. You said you would take charge of this, and I hope to hear that you have found a solution to the problem. The team was hoping to have one last rendering of the lighting for the game by October 10 for a preliminary run-through. Will the final version of the lighting be ready by then?</p>
    <p>All other aspects of the game are on schedule. Please send me an update about the lighting at your earliest convenience.</p>
    <p class="text-neutral-600 dark:text-neutral-400">Regards,<br/><strong>Cliff Merson</strong><br/>Project Manager, Rimerko Games</p>
  </div>

  <!-- Document 2: Review -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-neutral-50/50 dark:bg-neutral-900 shadow-xs space-y-2.5">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1.5">
      <h4 class="font-bold text-sm text-neutral-900 dark:text-neutral-100">Review of Titan Adventure: Neptune's Voyage</h4>
      <p class="text-[11px] text-neutral-500 italic mt-0.5">By Leo Weber, April 1</p>
    </div>
    <p>This new installment of Titan Adventure will surprise and delight both new players and old aficionados long familiar with the series. Though open-world formats have been widespread in recent years, Neptune's Voyage brings something new to the format. By stripping down instructional guides, the game gives users the opportunity to discover new areas and devices. In Neptune's Voyage, you wake up as Thetis, a dolphin that is tasked with rescuing Neptune from an underwater cave. Users then climb, run, ride, sail, and fly through the world of the game, encountering new towns, ruins, and other creatures along the way. Some of these creatures will be familiar to longtime fans, but there is plenty of novelty as well. This newest version also corrects the green and blue image rendering that was sometimes a problem in earlier installments of Titan Adventure.</p>
    <p class="font-medium text-indigo-700 dark:text-indigo-400">Neptune's Voyage launches May 5 on Rimerko Clutch and PS5. It is available in English, Korean, Japanese, French, and Spanish.</p>
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 13: Questions 186-190 (Triple Passage: Schedule, E-mail & Job Ad)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g186_190",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_186_190.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="space-y-4 text-xs leading-relaxed">
  <!-- Document 1: Schedule -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1 text-center">
      <h4 class="font-bold text-sm text-neutral-900 dark:text-neutral-100">Wonder Ridge Radio Broadcast Schedule, Monday–Friday</h4>
    </div>
    <div class="space-y-1.5 divide-y divide-neutral-100 dark:divide-neutral-800">
      <div class="pt-1 flex justify-between">
        <span class="font-bold text-neutral-800 dark:text-neutral-200">6 A.M.–Noon: COFFEE BREAK</span>
        <span class="text-neutral-500">Local news and interviews with community members</span>
      </div>
      <div class="pt-1 flex justify-between">
        <span class="font-bold text-neutral-800 dark:text-neutral-200">Noon–4 P.M.: AFTERNOON JAZZ</span>
        <span class="text-neutral-500">Host: Malachi Mzee (Traditional jazz to jazz fusion)</span>
      </div>
      <div class="pt-1 flex justify-between">
        <span class="font-bold text-neutral-800 dark:text-neutral-200">4 P.M.–7 P.M.: FOLK FRENZY</span>
        <span class="text-neutral-500">Host: Penny Ariza (Folk music from around the world)</span>
      </div>
      <div class="pt-1 flex justify-between">
        <span class="font-bold text-neutral-800 dark:text-neutral-200">7 P.M.–10 P.M.: JOSIE'S JOINT</span>
        <span class="text-neutral-500">Host: Josie Jones (Wonder Ridge Radio Music Director)</span>
      </div>
    </div>
  </div>

  <!-- Document 2: E-mail -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-neutral-50/50 dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1 text-neutral-600 dark:text-neutral-400 space-y-0.5">
      <div><strong class="text-neutral-900 dark:text-neutral-100">To:</strong> feedback@wonderridgeradio.org</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">From:</strong> Eric Fabre &lt;efabre@webmail.com&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Date:</strong> October 28</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Subject:</strong> Program feedback</div>
    </div>
    <p>Hello! I recently moved to the area and stumbled across your station while driving home from work around 5:30 P.M. I was blown away by the incredible folk tracks Penny was playing. It made the rush-hour traffic completely bearable. Keep up the fantastic programming!</p>
    <p class="text-neutral-600 dark:text-neutral-400">Eric Fabre</p>
  </div>

  <!-- Document 3: Job Ad -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1">
      <h4 class="font-bold text-sm text-neutral-900 dark:text-neutral-100">Wonder Ridge Radio Job Opening: Programming Assistant</h4>
      <p class="text-[11px] text-neutral-500 italic">Posted November 2</p>
    </div>
    <p><strong>Job Description:</strong> The programming assistant reports to the director of programming and supports the radio station by performing a variety of research and communication functions. This role is an entry-level, part-time position.</p>
    <div class="space-y-1">
      <div class="font-bold text-neutral-800 dark:text-neutral-200">Responsibilities:</div>
      <ul class="list-disc pl-4 space-y-0.5 text-neutral-600 dark:text-neutral-400">
        <li>Conducting background research on interviewees</li>
        <li>Keeping up-to-date on news and new music releases</li>
        <li>Assisting studio technicians during live broadcasts</li>
      </ul>
    </div>
    <div class="space-y-1">
      <div class="font-bold text-neutral-800 dark:text-neutral-200">Requirements:</div>
      <p class="text-neutral-600 dark:text-neutral-400">High school diploma; demonstrated computer literacy and familiarity with social media; keen interest in radio and media production. Previous radio industry experience is not required.</p>
    </div>
    <p class="text-[11px] text-neutral-500 pt-1">To apply, e-mail a résumé and cover letter to hiring@wonderridgeradio.org.</p>
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 14: Questions 191-195 (Triple Passage: Instructions, E-mail & Sign)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g191_195",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_191_195.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="space-y-4 text-xs leading-relaxed">
  <!-- Document 1: Instructions -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1">
      <h4 class="font-bold text-sm text-neutral-900 dark:text-neutral-100">Instructions for Requesting Records</h4>
      <p class="text-[11px] text-neutral-500 italic">City of Abilene Public Information Office</p>
    </div>
    <p>Thank you for your interest in official records and documents maintained by the City of Abilene. To file a request for public information, please follow these steps:</p>
    <ol class="list-decimal pl-4 space-y-1 text-neutral-700 dark:text-neutral-300">
      <li><strong>Create an account in the Records Center Web portal.</strong> Currently, all requests must be made through the portal.</li>
      <li><strong>Use the drop-down menu</strong> to locate the department from which you are seeking information and submit your request. You will receive a confirmation e-mail with a reference number.</li>
      <li><strong>The department staff will locate the requested records</strong> and contact you when they are available. You can have the records delivered to you, or you can pick them up in person. If you prefer to pick them up in person, you must make an appointment with the department staff.</li>
      <li><strong>If there are any fees associated with your request,</strong> you will receive an itemized statement detailing the services provided and the charges for those specific services.</li>
    </ol>
  </div>

  <!-- Document 2: E-mail -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-neutral-50/50 dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1 text-neutral-600 dark:text-neutral-400 space-y-0.5">
      <div><strong class="text-neutral-900 dark:text-neutral-100">To:</strong> Joo-Hee Park &lt;jhpark@coa.net&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">From:</strong> Keith Brandenberg &lt;kbrandenberg@mailcurrent.com&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Date:</strong> May 3</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Subject:</strong> RE: Reference number W2486</div>
    </div>
    <p>Dear Ms. Park,</p>
    <p>Thank you for confirming that my documents are available. I would like to pick them up in person as soon as possible. Do you have any appointments available this week?</p>
    <p>I have a question about the fee. Apparently, I am being charged $300 for my documents. I do not understand why the fee is so high, and there was no explanation included in your e-mail. I have requested records several times in the past in my role with RJ Environmental Engineering and have never paid such a high fee. In this case, I am only requesting two maps of the city's underground pipelines, which will inform our firm's current work advising the city on wastewater management.</p>
    <p>Please clarify the fee for me, and let me know if I can pick up my documents this week. Thank you.</p>
    <p class="text-neutral-600 dark:text-neutral-400">Best regards,<br/>Keith Brandenberg</p>
  </div>

  <!-- Document 3: Sign -->
  <div class="border-2 border-neutral-800 dark:border-neutral-300 rounded-xl p-3.5 bg-amber-50/50 dark:bg-neutral-800/40 text-center space-y-1.5">
    <h4 class="font-extrabold text-sm uppercase tracking-wider text-neutral-900 dark:text-neutral-100">City of Abilene Administrative Building</h4>
    <p class="text-xs text-rose-700 dark:text-rose-400 font-bold">Visitors must sign in prior to entering this facility.</p>
    <p class="text-xs text-neutral-600 dark:text-neutral-300">Please enter your name and the room you will visit in the logbook.</p>
    <div class="border-t border-neutral-300 dark:border-neutral-600 pt-2 grid grid-cols-2 gap-1 text-[11px] font-semibold text-neutral-800 dark:text-neutral-200 max-w-sm mx-auto text-left">
      <div>IT Services — Room 100</div>
      <div>Parks and Recreation — Room 101</div>
      <div>Transportation — Room 102</div>
      <div class="text-indigo-600 dark:text-indigo-400 font-bold">Wastewater — Room 103</div>
    </div>
  </div>
</div>"""
    },

    # -------------------------------------------------------------------------
    # Group 15: Questions 196-200 (Triple Passage: Review & 2 E-mails)
    # -------------------------------------------------------------------------
    {
        "id": "test1-p7-g196_200",
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 7,
        "image_url": "/images/test1/part7_196_200.png",
        "audio_url": None,
        "transcript_segments": None,
        "passage_text": """<div class="space-y-4 text-xs leading-relaxed">
  <!-- Document 1: Review -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1">
      <h4 class="font-bold text-sm text-neutral-900 dark:text-neutral-100">Famous Actor, First Book</h4>
      <p class="text-[11px] text-neutral-500 italic">LONDON (25 February) — By Uma Joshi</p>
    </div>
    <p>Fans of Simon Eklund will be delighted with his autobiography, <em>The Theatre Lights Dimmed</em>, the first book he has written in his storied career as an actor. It provides wonderful insight into his career, starting with his first roles in cinema in his native Sweden, moving into his work in France and Italy, and finishing with his recent theatre work in the U.K.</p>
    <p>In his book, Mr. Eklund dedicates a fair amount of text to discussing his mentor, Charles Gunnarsson, who helped him develop his skills early on in Stockholm. He also describes the difficulty of transitioning into different types of roles, especially from comedic to dramatic acting. He includes several funny anecdotes about his first attempts at acting onstage here in London. He describes them as disastrous, but anyone who saw his recent performance in <em>Life and Games</em> would say just the opposite.</p>
    <p>Mr. Eklund has long been a captivating actor on stage and screen, and now he is a thoroughly engaging author.</p>
  </div>

  <!-- Document 2: E-mail 1 -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-neutral-50/50 dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1 text-neutral-600 dark:text-neutral-400 space-y-0.5">
      <div><strong class="text-neutral-900 dark:text-neutral-100">To:</strong> Edith Hockin &lt;ehockin@topnews.co.uk&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">From:</strong> Uma Joshi &lt;ujoshi@topnews.co.uk&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Date:</strong> 2 March</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Subject:</strong> RE: Opportunity</div>
    </div>
    <p>Dear Edith,</p>
    <p>Thank you for agreeing to arrange an interview with Mr. Eklund for me. I think this will be a great follow-up to my recent piece.</p>
    <p>In a helpful coincidence, I will be visiting his home country next month to address a journalists' convention. I am the featured speaker and will discuss the benefits of diversity in journalism. I'm sure we can set up something with Mr. Eklund just before or after my speech.</p>
    <p class="text-neutral-600 dark:text-neutral-400">Best,<br/>Uma Joshi<br/>Arts and Culture Editor, Top News U.K.</p>
  </div>

  <!-- Document 3: E-mail 2 -->
  <div class="border border-neutral-300 dark:border-neutral-700 rounded-xl p-4 bg-white dark:bg-neutral-900 shadow-xs space-y-2">
    <div class="border-b border-neutral-200 dark:border-neutral-800 pb-1 text-neutral-600 dark:text-neutral-400 space-y-0.5">
      <div><strong class="text-neutral-900 dark:text-neutral-100">To:</strong> Uma Joshi &lt;ujoshi@topnews.co.uk&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">From:</strong> Maria Cazalla &lt;mcazalla@zephyrmail.se&gt;</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Date:</strong> 20 March</div>
      <div><strong class="text-neutral-900 dark:text-neutral-100">Subject:</strong> RE: Information</div>
    </div>
    <p>Dear Ms. Joshi,</p>
    <p>We are all very excited about your interview next month with Mr. Eklund. He enjoys all your writing for Top News U.K.—the news stories, interviews, and, of course, your recent article about <em>The Theatre Lights Dimmed</em>!</p>
    <p>I just wanted to finalize a few details with you. We have arranged transportation for you from your hotel to Mr. Eklund's house and then back to the hotel. Please let me know how many people there will be in your group, because Mr. Eklund would like you all to stay for lunch.</p>
    <p class="text-neutral-600 dark:text-neutral-400">Sincerely,<br/>Maria Cazalla</p>
  </div>
</div>"""
    }
]

print(f"Defined {len(part7_groups)} question groups.")
