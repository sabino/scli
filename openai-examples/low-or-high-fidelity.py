# low will enable the "low res" mode. The model will receive a low-res 512px x 512px version of the image,and represent the image with a budget of 85 tokens. This allows the API to return faster responses and consume fewer input tokens for use cases that do not require high detail.
# high will enable "high res" mode, which first allows the model to first see the low res image (using 85 tokens) and then creates detailed crops using 170 tokens for each 512px x 512px tile.

from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What’s in this image?"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            "detail": "high" # can be low or high
          },
        },
      ],
    }
  ],
  max_tokens=300,
)

print(response.choices[0].message.content)