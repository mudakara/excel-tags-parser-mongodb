# Claude Model 404 Error - Troubleshooting

## 🔴 Error

`API Error (404): model: claude-3-sonnet-20240229`

## 🎯 What This Means

A 404 error for a Claude model means one of these:

1. **Your API key doesn't have access to that specific model**
2. **The model requires a higher tier API access**
3. **Your account needs to be upgraded or verified**

This is NOT an error with the code - it's an API access issue.

## ✅ Solution: Try Different Models

### Option 1: Use Claude 3 Haiku (Most Accessible)

**Model:** `claude-3-haiku-20240307`

This is the most widely available Claude model and should work with most API keys:

1. Refresh the page
2. Select "Claude" as provider
3. Select **claude-3-haiku-20240307** from the dropdown
4. Try your query

**Why Haiku?**
- Available to all API tiers
- Fastest model
- Cheapest ($0.25-$1.25 per million tokens)
- Good for most queries

### Option 2: Use Claude 3.5 Sonnet (Latest)

**Model:** `claude-3-5-sonnet-20241022`

Try the latest model:

1. Select **claude-3-5-sonnet-20241022** from the dropdown
2. If you get 404, your API key doesn't have access yet

### Option 3: Use OpenRouter Instead

OpenRouter gives you access to Claude through their API:

1. Select **OpenRouter** as provider
2. Get API key from https://openrouter.ai/
3. Select **anthropic/claude-3.5-sonnet** as model
4. Works with all Claude models through OpenRouter

## 📊 Model Availability by API Tier

| Model | Free Tier | Paid Tier | Notes |
|-------|-----------|-----------|-------|
| claude-3-haiku-20240307 | ✅ Yes | ✅ Yes | Most accessible |
| claude-3-5-sonnet-20241022 | ⚠️ Maybe | ✅ Yes | Latest version |
| claude-3-5-sonnet-20240620 | ⚠️ Maybe | ✅ Yes | Older version |
| claude-3-opus-20240229 | ❌ No | ✅ Yes | Requires paid tier |
| claude-3-sonnet-20240229 | ⚠️ Maybe | ✅ Yes | Older version |

## 🔍 How to Check Your API Access

1. **Go to Claude Console:** https://console.anthropic.com/
2. **Check API Access:**
   - Settings → API
   - Look for "Model Access" or "Available Models"
3. **Check Billing:**
   - Settings → Billing
   - Ensure you have credits or a payment method

## 🚀 Recommended Order to Try

Try models in this order:

1. ✅ **claude-3-haiku-20240307** (Most likely to work)
2. **claude-3-5-sonnet-20241022** (Latest, if you have access)
3. **claude-3-5-sonnet-20240620** (Older but stable)
4. **claude-3-opus-20240229** (Requires paid tier)

## 💡 Quick Fix Steps

**Right now:**

1. **Refresh the page** in your browser
2. **Select Claude** as provider
3. **Look for the blue info box** that says "If you get a 404 error..."
4. **Select "claude-3-haiku-20240307"** from the dropdown
5. **Try your query**

This model has the highest chance of working!

## 🔧 Alternative: Use OpenRouter

If none of the Claude models work:

1. **Switch to OpenRouter:**
   - Provider: OpenRouter
   - API Key: Get from https://openrouter.ai/
   - Model: anthropic/claude-3.5-sonnet

2. **Benefits:**
   - Access to all Claude models
   - No tier restrictions
   - Pay per use
   - $5 credit is enough for testing

## 📞 If Still Not Working

If you still get 404 errors with ALL models:

1. **Verify API Key:**
   ```bash
   # Test with curl
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: YOUR_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{
       "model": "claude-3-haiku-20240307",
       "max_tokens": 100,
       "messages": [{"role": "user", "content": "Hi"}]
     }'
   ```

2. **Check Console:**
   - Go to https://console.anthropic.com/
   - Check if API access is enabled
   - Check if billing is set up

3. **Contact Support:**
   - Anthropic Support: support@anthropic.com
   - Check status: https://status.anthropic.com/

## ✅ Working Configuration

Here's a configuration that should work for most users:

```
Provider: Claude
API Key: sk-ant-your-key-here
Model: claude-3-haiku-20240307
```

or

```
Provider: OpenRouter
API Key: sk-or-v1-your-key-here
Model: anthropic/claude-3.5-sonnet
```

## 🎯 Summary

**The 404 error is NOT a bug** - it means your API key doesn't have access to that specific Claude model.

**Solution:** Use `claude-3-haiku-20240307` or switch to OpenRouter.

---

**Updated:** November 16, 2025
**Status:** Not a bug - API access limitation
**Fix:** Try different models or use OpenRouter
