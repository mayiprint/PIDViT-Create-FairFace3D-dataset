require 'torch'
require 'nn'
require 'nngraph'
require 'paths'

require 'image'
require 'xlua'
local utils = require 'utils'
local opts = require 'opts'(arg)
-- Load optional libraries
if opts.device == 'gpu' then require('cunn') end
if opts.device == 'gpu' then require('cudnn') end

-- Load optional data-loading libraries

local FaceDetector = require 'facedetection_dlib'

torch.setheaptracking(true)
torch.setdefaulttensortype('torch.FloatTensor')
torch.setnumthreads(1)

local fileList = utils.getFileList(opts)
local predictions = {}

local faceDetector = FaceDetector()

local model = torch.load(opts.model)
local modelZ
if opts.type == '3D-full' then
    modelZ = torch.load(opts.modelZ)
    if opts.device ~= 'cpu' then modelZ = modelZ:cuda() end
    modelZ:evaluate()
end
if opts.device == 'gpu' then model = model:cuda() end
model:evaluate()
for i = 1, #fileList do
    local img = image.load(fileList[i].image)
    --print(fileList[i].image)
    -- Convert grayscale to pseudo-rgb
    if img:size(1)==1 then
        img = torch.repeatTensor(img,3,1,1)
    end
    --print("o")
    -- Detect faces, if needed
    local detectedFaces, detectedFace
    if fileList[i].scale == nil then
        detectedFaces = faceDetector:detect(img)
	if(#detectedFaces<1) then goto continue end -- When continue is missing
	-- Compute only for the first face for now
        fileList[i].center, fileList[i].scale =	utils.get_normalisation(detectedFaces[1])
        detectedFace = detectedFaces[1]
    end
    --print("f")
    img = utils.crop(img, fileList[i].center, fileList[i].scale, 256):view(1,3,256,256)
    if opts.device ~= 'cpu' then img = img:cuda() end
    --print("t")
    local output = model:forward(img)[4]:clone()
    output:add(utils.flip(utils.shuffleLR(model:forward(utils.flip(img))[4])))
    local preds_hm, preds_img = utils.getPreds(output, fileList[i].center, fileList[i].scale)

    preds_hm = preds_hm:view(68,2):float()*4
    -- depth prediction
    if opts.type == '3D-full' then
        out = torch.zeros(68, 256, 256)
        for i=1,68 do
	        if preds_hm[i][1] > 0 then
        	    utils.drawGaussian(out[i], preds_hm[i], 2)
        	end
        end
        out = out:view(1,68,256,256)
        local inputZ = torch.cat(img:float(), out, 2)
        if opts.device ~= 'cpu' then inputZ = inputZ:cuda() end
        local depth_pred = modelZ:forward(inputZ):float():view(68,1) 
        preds_hm = torch.cat(preds_hm, depth_pred, 2)
    end

    if opts.mode == 'demo' then
        -- Converting it to the predicted space (for plotting)
        detectedFace[{{3,4}}] = utils.transform(torch.Tensor({detectedFace[3],detectedFace[4]}), fileList[i].center, fileList[i].scale, 256)
        detectedFace[{{1,2}}] = utils.transform(torch.Tensor({detectedFace[1],detectedFace[2]}), fileList[i].center, fileList[i].scale, 256)

        detectedFace[3] = detectedFace[3]-detectedFace[1]
        detectedFace[4] = detectedFace[4]-detectedFace[2]
        
        utils.plot(img, preds_hm, detectedFace)
    end
    print(fileList[i].image)
    if opts.save then
       local dest = opts.output..'/'..paths.basename(fileList[i].image, '.'..paths.extname(fileList[i].image))
       if opts.outputFormat == 't7' then
	   torch.save(dest..'.t7', preds_img)
       elseif opts.outputFormat == 'txt' then
	   -- csv without header
	   local out = torch.DiskFile(dest .. '.txt', 'w')
	   for i=1,68 do
	      out:writeString(tostring(preds_img[{1,i,1}]) .. ',' .. tostring(preds_img[{1,i,2}]) .. '\n')
	   end
	   out:close()
       end
    end


    if opts.mode == 'eval' then
        predictions[i] = preds_img:clone() + 1.75
        xlua.progress(i,#fileList)
    end
    ::continue::
end

if opts.mode == 'eval' then
    predictions = torch.cat(predictions,1)
    local dists = utils.calcDistance(predictions,fileList)
    utils.calculateMetrics(dists)
end
