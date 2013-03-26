	$(document).ready(function(){
	    	jdata=data();
				
				var keys = Object.keys(jdata);
				keys.sort();
				
				first_date = keys[0]
				first_date_d = new Date(first_date)
				
				keys.reverse()
				latest_date = keys[0]
				latest_date_d = new Date(latest_date);

				var enrolled_time = extractTimeData(jdata,
												"enrolled",
												group = "location")
				var ps = extractTimeData(jdata,
										"patient_source",
										group = "text")
				
				//pie_chart(ps[latest_date_d.getTime()],"chart_pie")

				// *** PROGRAMME INDICATORS ***

				// Enrolled
				total_enrolled = total_time_data(enrolled_time,1)[latest_date_d.getTime()]
				enrolled_percent_change=percent_change(enrolled_time,1,"total");
				$('#enrolledPatients').html('<h1 class="dashnum">' + addCommas(total_enrolled) + '</h1>');
				if (enrolled_percent_change > 0) {
					$('#enrolledPatientsPercent').html('<h2 class="dashnum text-success">(+' + enrolled_percent_change + '%)</h2>');
				} else {
					$('#enrolledPatientsPercent').html('<h2 class="dashnum text-error">(' + enrolled_percent_change + '%)</h2>');
				}

				// On ART
				var on_art_time = extractTimeData(jdata,
													"on_art_who",
													group = "text")
				total_on_art = total_time_data(on_art_time,1)[latest_date_d.getTime()]
				percent_change_on_art = percent_change(on_art_time,1,"total");
				$('#onArt').html('<h1 class="dashnum">' + addCommas(total_on_art) + '</h1>');
				if (percent_change_on_art > 0) {
					$('#onArtPercent').html('<h2 class="dashnum text-success">(+' + percent_change_on_art + '%)</h2>');
				} else {
					$('#onArtPercent').html('<h2 class="dashnum text-error">(' + percent_change_on_art + '%)</h2>');
				}

				// Eligible not on ART
				var eligible_not_on_art_time = extractTimeData(jdata,
																"eligible_no_art",
																group="location")
				total_eligible_not_on_art = total_time_data(eligible_not_on_art_time,1)[latest_date_d.getTime()]
				percent_change_eligible_not_on_art = percent_change(eligible_not_on_art_time,1,"total");
				$('#eligibleNotOnArt').html('<h1 class="dashnum">' + addCommas(total_eligible_not_on_art) + '</h1>');
				if (percent_change_eligible_not_on_art > 0) {
					$('#eligibleNotOnArtPercent').html('<h2 class="dashnum text-error">(+' + percent_change_eligible_not_on_art + '%)</h2>');
				} else {
					$('#eligibleNotOnArtPercent').html('<h2 class="dashnum text-success">(' + percent_change_eligible_not_on_art + '%)</h2>');
				}

				// Lost to followup
				var exit_care_time = extractTimeData(jdata,
													"inactive_reason",
													group="text")
				lost_to_followup_time = {}
				for (key in exit_care_time){
					lost_to_followup_time[key] = exit_care_time[key]["LOST TO FOLLOWUP"]
				}
				total_lost_to_followup = lost_to_followup_time[latest_date_d.getTime()];
				percent_change_lost_to_followup = Math.round((lost_to_followup_time[latest_date_d.getTime()] - lost_to_followup_time[first_date_d.getTime()]) / lost_to_followup_time[first_date_d.getTime()] * 100)
				$('#lostToFollowup').html('<h1 class="dashnum">' + addCommas(total_lost_to_followup) + '</h1>');
				if (percent_change_lost_to_followup > 0) {
					$('#lostToFollowupPercent').html('<h2 class="dashnum text-error">(+' + percent_change_lost_to_followup + '%)</h2>');
				} else {
					$('#lostToFollowupPercent').html('<h2 class="dashnum text-success">(' + percent_change_lost_to_followup + '%)</h2>');
				}

				// Followed up
				var followed_up_time = extractTimeData(jdata,
														"followed_up",
														group="location")
				total_followed_up = total_time_data(followed_up_time,1)[latest_date_d.getTime()]
				$('#lostPatientsFollowedUp').html('<h1 class="dashnum">' + addCommas(total_followed_up) + '</h1>');

				// Last updated
				$('#lastDate').html(latest_date_d.getDate()+'/'+latest_date_d.getMonth()+'/'+latest_date_d.getFullYear());

				// *** CHARTS ***
				
				// Timeline chart
				scaling=total_time_data(enrolled_time,1) // Get scaling for line chart
				timeline_nv(enrolled_time,"chart_nv");

				// Missing data chart
				var missing_data = extractTimeData(jdata,"missing",group="text")
				missing_data_scaled = scale(missing_data,scaling,100,2)
				missing_percent_change = percent_change(missing_data_scaled,1,"individual");
				horizontal_bar_chart(missing_percent_change,"bar_chart")
				line_chart(missing_data,"line_chart",scaling);
				
				/*
				$("#enrolled").html(table(jdata[latest_date]["enrolled"],false));
				$("#patient_source").html(table(jdata[latest_date]["patient_source"],true));
				$("#eligibility_for_art").html(table(jdata[latest_date]["eligible_no_art"],false));
				$("#who_on_art").html(table(jdata[latest_date]["on_art_who"],true));
				$("#exciting_care").html(table(jdata[latest_date]["inactive_reason"],true));
				$("#follow_up").html(table(jdata[latest_date]["reason_to_follow_up"],true));
				$("#followed_up").html(table(jdata[latest_date]["followed_up"],false));      
				$("#willing_to_return").html(table(jdata[latest_date]["willing_to_return"],false));
				$("#missing_data").html(table(jdata[latest_date]["missing"],true));
				*/
			});
		
