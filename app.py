import streamlit as st
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
import os
import time

# Set up page title and layout
st.set_page_config(page_title='Music Mixing Website')
st.title('Music Mixing Website')

# Define functions for loading and playing audio files
def load_audio_file(file_path):
    audio, sr = librosa.load(file_path, sr=44100, mono=True)
    return audio, sr

def play_audio_file(file_path):
    audio, sr = load_audio_file(file_path)
    st.audio(audio, format='audio/wav')

# Define functions for mixing audio files
def mix_audio_files(file_paths, mix_ratios):
    mixed_audio, sr = load_audio_file(file_paths[0])
    for i in range(1, len(file_paths)):
        audio_i, sr_i = load_audio_file(file_paths[i])
        audio_i_resampled = librosa.resample(audio_i, sr_i, sr)
        mixed_audio = (mixed_audio * (1 - mix_ratios[i-1])) + (audio_i_resampled * mix_ratios[i-1])
    return mixed_audio, sr

# Define functions for applying audio effects and filters
def apply_audio_effects(audio, sr, effect_type, effect_params):
    if effect_type == 'reverb':
        return librosa.effects.reverb(audio, **effect_params), sr
    elif effect_type == 'delay':
        return librosa.effects.delay(audio, sr, **effect_params), sr
    elif effect_type == 'distortion':
        return librosa.effects.harmonic(audio, **effect_params), sr
    elif effect_type == 'eq':
        return librosa.effects.equalize(audio, **effect_params), sr
    else:
        return audio, sr

# Define Streamlit widgets for uploading and mixing audio files
st.sidebar.title('Upload Audio Files')
uploaded_files = st.sidebar.file_uploader('Upload Audio Files:', type=['mp3', 'wav'], accept_multiple_files=True)

# Mix audio files when at least two files are uploaded
if len(uploaded_files) >= 2:
    st.sidebar.title('Mixing Settings')
    mix_ratios = []
    for i in range(len(uploaded_files)-1):
        mix_ratios.append(st.sidebar.slider(f'Mix Ratio {i+1}/{len(uploaded_files)-1}:', min_value=0.0, max_value=1.0, value=0.5, step=0.1))

    # Mix audio files and apply audio effects and filters
    mixed_audio, sr = mix_audio_files([file.name for file in uploaded_files], mix_ratios)
    st.success('Audio files mixed successfully!')
    st.audio(mixed_audio, format='audio/wav')

    st.sidebar.title('Audio Effects')
    effect_type = st.sidebar.selectbox('Select Audio Effect:', options=['None', 'Reverb', 'Delay', 'Distortion', 'EQ'])
    if effect_type != 'None':
        effect_params = {}
        if effect_type == 'Reverb':
            effect_params['room_size'] = st.sidebar.slider('Room Size:', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
            effect_params['damping'] = st.sidebar.slider('Damping:', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
            effect_params['wet_gain'] = st.sidebar.slider('Wet Gain:', min_value=0)
    elif effect_type == 'Delay':
        effect_params['delay_time'] = st.sidebar.slider('Delay Time:', min_value=0, max_value=1000, value=500, step=10)
        effect_params['decay_ratio'] = st.sidebar.slider('Decay Ratio:', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
    elif effect_type == 'Distortion':
        effect_params['amount'] = st.sidebar.slider('Amount:', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        effect_params['per_channel'] = True
    elif effect_type == 'EQ':
        effect_params['center_freqs'] = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 16000]
        effect_params['bandwidths'] = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 16000]
        effect_params['gain_db'] = st.sidebar.slider('Gain (dB):', min_value=-20.0, max_value=20.0, value=0.0, step=1.0)

    mixed_audio, sr = apply_audio_effects(mixed_audio, sr, effect_type.lower(), effect_params)
    st.success(f'{effect_type} applied successfully!')
    st.audio(mixed_audio, format='audio/wav')

st.sidebar.title('Save Audio File')
file_name = st.sidebar.text_input('Enter file name:', value='mixed_audio')
file_format = st.sidebar.selectbox('Select file format:', options=['wav', 'mp3'])
save_file_button = st.sidebar.button('Save Audio File')

if save_file_button:
    with st.spinner('Saving audio file...'):
        file_path = f'{file_name}.{file_format}'
        sf.write(file_path, mixed_audio, sr)
        st.success(f'Audio file saved as {file_path}!')
else:
st.warning('Upload at least two audio files to begin mixing!')
