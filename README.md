This is a Python Script to run a metronome with a few useful features:
1.) Any time signature can be played in the metronome. Just type the number of beats.
2.) Any subdivision can be played. You can also set different subdivisions for each beat. Those subdivisions need to be separated by commas.
3.) Subdivisions can span beats. These need to be written out as fractions. For example, if you have 8 total beats, you can write 5/3,5/3,3/2 and 5 sub beats will span the first three
    beats, 5 sub beats will span the next 3 beats, and 3 sub beats will span the last 2 beats.
4.) A subdivision of zero will keep the time, but not play any sound. With 4 beats, if you list subdivisions as 1,0,1,1, clicks will only happen on 1, 3, and 4.

There are a few unresolved issues currently:
1.) A strong beat can only be played on the 1.
2.) The metronome needs to be stopped before the inputs are changed; pressing start again will overlap the two.
