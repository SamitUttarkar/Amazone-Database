[
    {
        $match: {
        _id: /W/,
        },
    },
    {  $unwind: {
        path: "$realtime_inventory",
        },
    },
    {    $match: {
        "realtime_inventory.quantity": 0,
        },
    },
    {    $lookup: {
        from: "products",
        localField: "realtime_inventory.product_id",
        foreignField: "_id",
        as: "product_detail",
        },
    },
    {    $unwind: {
        path: "$product_detail",
        },
    },
    {    $project: {
        _id: 0,
        warehouse_name: "$name",
        product_category: "$product_detail.category",
        product_name: "$product_detail.name",
        warehouse_address: "$address",
        post_code: "$post_code",
        city: "$city",
        },
    }
]